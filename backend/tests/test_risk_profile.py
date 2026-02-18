from app.models.risk import RiskProfile


def test_risk_profile_defaults() -> None:
    profile = RiskProfile(submission_id="sub_test")
    assert profile.submission_id == "sub_test"
    assert profile.locations == []
    assert profile.prior_losses == []
    assert profile.version == 1
