"""Synthetic-only identity conformance. FixtureBoundary is NOT an authority service."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from validate import ContractError, NAMES, SCHEMA, bounded, read_json, validate

ROOT_HASH = 'sha256:' + 'a' * 64

def digest(record):
    # Test-only commitment, NOT canonical OpenRGD source hashing or a signature.
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def fixture():
    def item(kind, **fields):
        return dict(schema_version='openrgd_identity_v0.1-candidate', record_type=kind,
                    record_id='fixture:record:' + kind, issuer_ref='fixture:authority',
                    proof_refs=['fixture:receipt:' + kind], grants_authority=False, **fields)
    return {
        'life': item('LifeIdentity', life_id='fixture:life:one', assurance='ATTESTED_CLAIM',
                     state='ACTIVE', custody_ref='fixture:custody', creation='EXPLICIT_ENROLLMENT',
                     predecessor_life_id=None),
        'agent': item('AgentDescriptor', agent_id='fixture:agent:writer', life_id='fixture:life:one',
                      role='HISTORY_WRITER', requested_capability_refs=[]),
        'binding': item('RobotLifeBinding', binding_id='fixture:binding', life_id='fixture:life:one',
                        robot_id='fixture:robot', robot_enrollment_ref='fixture:enrollment',
                        source_root=ROOT_HASH, forge_id=None, artifact_id=None, state='DECLARED'),
        'activation': item('LifeActivation', activation_id='fixture:activation', life_id='fixture:life:one',
                           binding_id='fixture:binding', life_activation_epoch=7, state='ACTIVE_CLAIM'),
        'runtime': item('RuntimeInstance', runtime_instance_id='fixture:runtime:one',
                        agent_id='fixture:agent:writer', boot_id='fixture:boot:one', session_id='fixture:session:one',
                        scope='LIFE_BOUND', life_id='fixture:life:one', life_binding_ref='fixture:binding',
                        life_activation_epoch=7, source_root=ROOT_HASH, policy_revision='fixture:policy:one',
                        model_revision='fixture:model:one', transition='INITIALIZE',
                        predecessor_runtime_ref=None, checkpoint_ref=None),
        'lease': item('RoleLease', lease_id='fixture:lease:one', life_id='fixture:life:one',
                      binding_id='fixture:binding', life_activation_epoch=7, role='HISTORY_WRITER',
                      scope_ref='fixture:ledger', owner_agent_id='fixture:agent:writer',
                      runtime_instance_id='fixture:runtime:one', role_fencing_generation=10,
                      clock_domain='fixture:authority-clock', valid_from_ms=10, valid_until_ms=1000),
        'status': item('ContinuityStatus', assessment_id='fixture:assessment', life_id=None,
                       runtime_instance_id='fixture:runtime:one', state='UNKNOWN',
                       reason_codes=['NOT_VERIFIED'], evidence_refs=[], checkpoint_ref=None,
                       history_watermark_ref=None, physical_execution_authorized=False),
    }

class FixtureBoundary:
    """Exact-record receipts and current receiver state supplied by a TEST authority.

    No cryptography, distributed lease store, hardware, registry or persistent writer.
    A caller controlling this object controls all trust: never use as a real verifier.
    """
    def __init__(self, bundle):
        self.receipts = {v['record_id']: digest(v) for v in bundle.values()}
        self.current = (10, 'fixture:runtime:one')
        self.policy = 'fixture:policy:one'
        self.root = ROOT_HASH
        self.life = 'fixture:life:one'
        self.epoch = 7
        self.online = True
        self.custody_available = True
        self.revoked = set()
        self.enrollment = ('fixture:enrollment', 'fixture:robot')
        self.watermark = 'fixture:history:100'
        self.checkpoints = {}
        self.fork_approved = False
        self.migration_approved = False
        self.grant_active = False
        self.accepted = set()

    def accept(self, b, *, now=100, clock='fixture:authority-clock',
               scope='fixture:ledger', category='INTERNAL_READ_ONLY', key='fixture:request:one'):
        # Refresh receiver-side authority on EVERY operation, never cached claims.
        if not self.online:
            raise ContractError('AUTHORITY_UNAVAILABLE')
        if not self.custody_available:
            raise ContractError('RECOVERY_REQUIRED')
        for name in ('life', 'agent', 'binding', 'activation', 'runtime', 'lease'):
            if name not in b:
                raise ContractError('RECOVERY_REQUIRED')
            value = validate(b[name])
            if value['issuer_ref'] != 'fixture:authority' or not value['proof_refs']:
                raise ContractError('PROOF_REQUIRED')
            if value['record_id'] in self.revoked or self.receipts.get(value['record_id']) != digest(value):
                raise ContractError('RECEIPT_MISMATCH_OR_REVOKED')
        life, agent, binding, active, rt, lease = (b[k] for k in ('life','agent','binding','activation','runtime','lease'))
        if life['assurance'] != 'ATTESTED_CLAIM':
            raise ContractError('LOCAL_PROVISIONAL_ONLY')
        if any(v['life_id'] != self.life for v in (life,agent,binding,active,rt,lease)):
            raise ContractError('LIFE_MISMATCH')
        if life['state'] != 'ACTIVE' or binding['state'] != 'DECLARED' or active['state'] != 'ACTIVE_CLAIM':
            raise ContractError('REVOKED')
        if (binding['robot_enrollment_ref'], binding['robot_id']) != self.enrollment:
            raise ContractError('ENROLLMENT_MISMATCH')
        if life['custody_ref'] != 'fixture:custody':
            raise ContractError('CUSTODY_MISMATCH')
        if any(x != binding['binding_id'] for x in (active['binding_id'],rt['life_binding_ref'],lease['binding_id'])):
            raise ContractError('BINDING_MISMATCH')
        if any(x != self.epoch for x in (active['life_activation_epoch'],rt['life_activation_epoch'],lease['life_activation_epoch'])):
            raise ContractError('ACTIVATION_MISMATCH')
        if rt['scope'] != 'LIFE_BOUND' or rt['agent_id'] != agent['agent_id'] or lease['owner_agent_id'] != agent['agent_id']:
            raise ContractError('OWNER_MISMATCH')
        if lease['runtime_instance_id'] != rt['runtime_instance_id'] or agent['role'] != lease['role']:
            raise ContractError('ROLE_MISMATCH')
        if scope != lease['scope_ref'] or clock != lease['clock_domain']:
            raise ContractError('SCOPE_OR_CLOCK_MISMATCH')
        if type(now) is not int or not lease['valid_from_ms'] <= now < lease['valid_until_ms']:
            raise ContractError('LEASE_EXPIRED_OR_FUTURE')
        if (lease['role_fencing_generation'],rt['runtime_instance_id']) != self.current:
            raise ContractError('STALE_OR_CONFLICTING_OWNER')
        if binding['source_root'] != self.root or rt['source_root'] != self.root or rt['policy_revision'] != self.policy:
            raise ContractError('CONTEXT_CHANGED')
        if rt['transition'] == 'RESTORE' and self.checkpoints.get(rt['checkpoint_ref']) != (self.life,self.watermark):
            raise ContractError('RESTORE_WATERMARK_MISMATCH')
        if rt['transition'] == 'FORK' and not (self.fork_approved and life['creation'] == 'EXPLICIT_FORK' and life['predecessor_life_id'] != life['life_id']):
            raise ContractError('FORK_REVIEW_REQUIRED')
        if rt['transition'] == 'MIGRATION' and not self.migration_approved:
            raise ContractError('MIGRATION_REVIEW_REQUIRED')
        if rt['transition'] == 'REBOOT' and (not rt['predecessor_runtime_ref'] or rt['predecessor_runtime_ref'] == rt['runtime_instance_id']):
            raise ContractError('REBOOT_PREDECESSOR_REQUIRED')
        if category != 'INTERNAL_READ_ONLY':
            if category != 'HISTORY_COMMIT_REQUEST' or not self.grant_active:
                raise ContractError('SEPARATE_EFFECT_GRANT_REQUIRED')
            marker = (self.life, scope, key)
            if marker in self.accepted:
                raise ContractError('DUPLICATE_REQUEST')
            self.accepted.add(marker)  # volatile TEST dedup, not a durable ledger write
        return {'life_id':life['life_id'], 'runtime_instance_id':rt['runtime_instance_id'],
                'life_binding_ref':binding['binding_id'], 'life_activation_epoch':self.epoch,
                'role_fencing_generation':lease['role_fencing_generation'],
                'identity_verification':'FIXTURE_ONLY', 'physical_execution_authorized':False}

class Tests(unittest.TestCase):
    def setUp(self):
        self.b=fixture(); self.a=FixtureBoundary(self.b)
    def resign(self, name):
        self.a.receipts[self.b[name]['record_id']]=digest(self.b[name])
    def test_candidate_status(self):
        s=read_json(Path(__file__).parent/'STATUS.json')
        self.assertEqual(s['maturity'],'candidate')
        for k in ('normative','accepted','runtime_implemented','stable_release_allowed'):self.assertIs(s[k],False)
    def test_seven_shapes(self):self.assertEqual(len(NAMES),7)
    def test_receipts_do_not_grant_effects(self):
        self.a.accept(self.b)
        with self.assertRaises(ContractError):self.a.accept(self.b,category='HISTORY_COMMIT_REQUEST')
    def test_reboot_preserves_life_activation_not_fence(self):
        old=deepcopy(self.b)
        rt=self.b['runtime'];rt.update(runtime_instance_id='fixture:runtime:two',boot_id='fixture:boot:two',
            session_id='fixture:session:two',transition='REBOOT',predecessor_runtime_ref='fixture:runtime:one')
        self.b['lease'].update(runtime_instance_id=rt['runtime_instance_id'],role_fencing_generation=11)
        self.resign('runtime');self.resign('lease');self.a.current=(11,rt['runtime_instance_id'])
        result=self.a.accept(self.b)
        self.assertEqual((result['life_id'],result['life_activation_epoch']),('fixture:life:one',7))
        with self.assertRaises(ContractError):self.a.accept(old)
    def test_model_swap_preserves_life(self):
        self.b['runtime']['model_revision']='fixture:model:two';self.resign('runtime')
        self.assertEqual(self.a.accept(self.b)['life_id'],'fixture:life:one')
    def test_receiver_fences_previously_valid_writer(self):
        self.a.accept(self.b); self.a.current=(11,'fixture:runtime:two')
        with self.assertRaises(ContractError):self.a.accept(self.b)
    def test_partition(self):
        self.a.online=False
        with self.assertRaisesRegex(ContractError,'AUTHORITY_UNAVAILABLE'):self.a.accept(self.b)
    def test_missing_custody(self):
        self.a.custody_available=False
        with self.assertRaisesRegex(ContractError,'RECOVERY_REQUIRED'):self.a.accept(self.b)
    def test_missing_record_no_auto_creation(self):
        del self.b['life'];before=deepcopy(self.b)
        with self.assertRaises(ContractError):self.a.accept(self.b)
        self.assertEqual(before,self.b)
    def test_no_record_mutation(self):
        before=deepcopy(self.b);self.a.accept(self.b);self.assertEqual(before,self.b)
    def test_revocation_after_first_use(self):
        self.a.accept(self.b);self.a.revoked.add(self.b['lease']['record_id'])
        with self.assertRaises(ContractError):self.a.accept(self.b)
    def test_expiry_boundary(self):
        self.a.accept(self.b,now=999)
        with self.assertRaises(ContractError):self.a.accept(self.b,now=1000)
    def test_lease_does_not_extend_itself(self):
        self.b['lease']['valid_until_ms']=9999
        with self.assertRaises(ContractError):self.a.accept(self.b)
    def test_history_idempotency(self):
        self.a.grant_active=True;self.a.accept(self.b,category='HISTORY_COMMIT_REQUEST')
        with self.assertRaises(ContractError):self.a.accept(self.b,category='HISTORY_COMMIT_REQUEST')
    def test_revoked_effect_grant_not_restored(self):
        self.a.grant_active=True;self.a.accept(self.b,category='HISTORY_COMMIT_REQUEST');self.a.grant_active=False
        with self.assertRaises(ContractError):self.a.accept(self.b,category='HISTORY_COMMIT_REQUEST',key='fixture:two')
    def test_unknown_or_foreign_effects(self):
        self.a.grant_active=True
        for cat in ['COMMUNICATION_REQUEST','DIGITAL_EFFECT_REQUEST','PHYSICAL_ACTION_REQUEST','UNKNOWN']:
            with self.subTest(cat=cat),self.assertRaises(ContractError):self.a.accept(self.b,category=cat)
    def test_restore_validates_watermark(self):
        self.b['runtime'].update(transition='RESTORE',checkpoint_ref='fixture:checkpoint');self.resign('runtime')
        self.a.checkpoints['fixture:checkpoint']=(self.a.life,self.a.watermark);self.a.accept(self.b)
        self.a.watermark='fixture:history:101'
        with self.assertRaises(ContractError):self.a.accept(self.b)
    def test_schema_valid_claim_is_not_proof(self):
        self.b['life']['proof_refs']=['fixture:invented'];validate(self.b['life'])
        with self.assertRaises(ContractError):self.a.accept(self.b)
    def test_forged_status_cannot_fix_missing_custody(self):
        self.b['status'].update(state='CONTINUITY_CLAIMED',life_id='fixture:life:one',evidence_refs=['fixture:fake'])
        validate(self.b['status']);self.a.custody_available=False
        with self.assertRaises(ContractError):self.a.accept(self.b)
    def test_metadata_publication_not_enrollment(self):
        self.b['binding'].update(forge_id='fixture:forge',artifact_id='fixture:publication',robot_enrollment_ref='fixture:invented');self.resign('binding')
        with self.assertRaises(ContractError):self.a.accept(self.b)
    def test_offline_no_process_no_network(self):
        with patch.object(socket,'socket',side_effect=AssertionError('network')),patch.object(subprocess,'Popen',side_effect=AssertionError('process')):
            for value in self.b.values():validate(value)
            self.a.accept(self.b)
    def test_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"x":1,"x":2}')
            with self.assertRaises(ContractError):read_json(p)
    def test_nonfinite(self):
        for v in [float('nan'),float('inf')]:
            with self.assertRaises(ContractError):bounded({'x':v})
    def test_resource_bounds(self):
        for v in [{'x':'a'*140000},[[0]*5000]]:
            with self.assertRaises(ContractError):bounded(v)
    def test_cycles_bounded(self):
        x=[];x.append(x)
        with self.assertRaises(ContractError):bounded(x)
    def test_source_revision_update_preserves_life(self):
        self.a.root='sha256:'+'d'*64
        self.b['binding']['source_root']=self.a.root;self.b['runtime']['source_root']=self.a.root
        self.resign('binding');self.resign('runtime')
        self.assertEqual(self.a.accept(self.b)['life_id'],'fixture:life:one')
    def test_session_scoped_shape_does_not_create_life(self):
        self.b['runtime'].update(scope='SESSION_SCOPED',life_id=None,life_binding_ref=None,life_activation_epoch=None)
        validate(self.b['runtime']);self.resign('runtime')
        with self.assertRaises(ContractError):self.a.accept(self.b)
    def test_self_fork(self):
        self.b['life'].update(creation='EXPLICIT_FORK',predecessor_life_id='fixture:life:one')
        with self.assertRaises(ContractError):validate(self.b['life'])
    def test_invalid_interval(self):
        self.b['lease'].update(valid_from_ms=100,valid_until_ms=100)
        with self.assertRaises(ContractError):validate(self.b['lease'])
    def test_counter_overflow(self):
        self.b['lease']['role_fencing_generation']=2147483648
        with self.assertRaises(ContractError):validate(self.b['lease'])
    def test_unknown_version(self):
        self.b['runtime']['schema_version']='openrgd_identity_v9'
        with self.assertRaises(ContractError):validate(self.b['runtime'])
    def test_restore_without_checkpoint(self):
        self.b['runtime']['transition']='RESTORE'
        with self.assertRaises(ContractError):validate(self.b['runtime'])
    def test_attested_claim_requires_reference_not_secret(self):
        self.b['life']['proof_refs']=[]
        with self.assertRaises(ContractError):validate(self.b['life'])
    def test_core_b_context_shape(self):
        path=os.environ.get('CORE_B_SCHEMA')
        if not path:
            self.skipTest('Core-B snapshot unavailable locally; CI MUST set CORE_B_SCHEMA')
        from jsonschema import Draft202012Validator
        b=json.loads(Path(path).read_text());view=self.a.accept(self.b)
        context={'revision':'sha256:'+'b'*64,'policy_revision':self.a.policy,
                 'session_id':self.b['runtime']['session_id'],'runtime_instance_id':view['runtime_instance_id'],
                 'scope':'LIFE_BOUND','life_binding_ref':view['life_binding_ref'],
                 'life_activation_epoch':view['life_activation_epoch'],
                 'role_fencing_generation':view['role_fencing_generation']}
        Draft202012Validator({'$defs':b['$defs'],'$ref':'#/$defs/Context'}).validate(context)

# Authenticated-but-inconsistent records exercise cross-record semantics, not just shapes.
SEMANTIC_NEGATIVES = [
 ('life','assurance','LOCAL_PROVISIONAL'),('life','state','REVOKED'),('life','life_id','fixture:other'),
 ('life','custody_ref','fixture:other'),('agent','life_id','fixture:other'),('agent','role','INFERENCE_WORKER'),
 ('binding','life_id','fixture:other'),('binding','robot_id','fixture:other'),('binding','state','REVOKED'),
 ('binding','source_root','sha256:'+'c'*64),('activation','binding_id','fixture:other'),
 ('activation','life_activation_epoch',8),('activation','state','REVOKED'),
 ('runtime','agent_id','fixture:other'),('runtime','life_id','fixture:other'),
 ('runtime','life_binding_ref','fixture:other'),('runtime','life_activation_epoch',8),
 ('runtime','source_root','sha256:'+'c'*64),('runtime','policy_revision','fixture:old-policy'),
 ('runtime','transition','MIGRATION'),('runtime','transition','FORK'),('runtime','transition','REBOOT'),
 ('lease','binding_id','fixture:other'),('lease','owner_agent_id','fixture:other'),
 ('lease','runtime_instance_id','fixture:old-runtime'),('lease','role_fencing_generation',9),
 ('lease','life_activation_epoch',8),('lease','scope_ref','fixture:other-ledger'),
 ('lease','clock_domain','fixture:other-clock'),('lease','valid_until_ms',99),('lease','valid_from_ms',101)]
def negative(name,key,value):
    def test(self):
        self.b[name][key]=value;validate(self.b[name]);self.resign(name)
        with self.assertRaises(ContractError):self.a.accept(self.b)
    return test
for i,(name,key,value) in enumerate(SEMANTIC_NEGATIVES):
    setattr(Tests,f'test_semantic_{i:02}_{name}_{key}',negative(name,key,value))
for name in fixture():
    def shape(self,name=name):validate(self.b[name])
    def unknown(self,name=name):
        self.b[name]['unauthorized_field']=True
        with self.assertRaises(ContractError):validate(self.b[name])
    def grant(self,name=name):
        self.b[name]['grants_authority']=True
        with self.assertRaises(ContractError):validate(self.b[name])
    setattr(Tests,'test_positive_'+name,shape)
    setattr(Tests,'test_unknown_field_'+name,unknown)
    setattr(Tests,'test_self_grant_'+name,grant)
if __name__=='__main__':unittest.main(verbosity=2)
