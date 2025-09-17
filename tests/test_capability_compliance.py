from prop.compliance import build_compliance_matrix

def test_capability_compliance_basic():
    required = ["cloud", "devops", "cyber"]
    sections = ["Cloud Migration Plan", "DevSecOps Pipeline", "Program Management"]
    rows = build_compliance_matrix(required, sections)
    by_req = {r['Requirement']: r for r in rows}
    assert by_req['cloud']['Coverage'] == 'Yes'
    assert by_req['devops']['Coverage'] == 'Yes'  # substring match
    assert by_req['cyber']['Coverage'] == 'Gap'
