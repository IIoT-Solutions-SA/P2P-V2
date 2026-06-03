"""
Comprehensive backend validation test suite.
Tests all security patterns, length constraints, list limits, and numeric bounds.
Run with: python test_validation.py
"""
from app.schemas.usecase import (
    UseCaseCreate, UseCaseDraftCreate,
    QuantitativeResult, ChallengeSolution,
)
from app.schemas.forum import ForumPostCreate
from app.api.v1.endpoints.forum import ReplyCreate, PostUpdate
from app.api.v1.endpoints.usecases import UseCaseUpdate as EndpointUseCaseUpdate
from app.core.input_validation import check_safe_text, check_safe_tag
from pydantic import ValidationError

passed = 0
failed = 0

def expect_safe_text_to_reject(value):
    """Expect check_safe_text to raise ValueError (reject the input)"""
    try:
        check_safe_text(value)
        raise AssertionError(f"Expected ValueError for: {value}")
    except ValueError:
        pass  # Expected

def expect_safe_text_to_accept(value):
    """Expect check_safe_text to return the value (accept the input)"""
    result = check_safe_text(value)
    if result != value:
        raise AssertionError(f"Expected '{value}' to pass, got '{result}'")

def expect_tag_to_reject(value):
    """Expect check_safe_tag to raise ValueError (reject the tag)"""
    try:
        check_safe_tag(value)
        raise AssertionError(f"Expected ValueError for tag: {value}")
    except ValueError:
        pass  # Expected

def expect_tag_to_accept(value):
    """Expect check_safe_tag to pass (accept the tag)"""
    check_safe_tag(value)

def expect_validation_error(schema, data):
    """Expect Pydantic schema creation to raise ValidationError"""
    try:
        schema(**data)
        raise AssertionError(f"Expected ValidationError but schema accepted: {data}")
    except ValidationError:
        pass  # Expected

def expect_schema_ok(schema, data):
    """Expect Pydantic schema creation to succeed"""
    try:
        return schema(**data)
    except ValidationError as e:
        raise AssertionError(f"Expected success but got: {e.errors()}")

def run_test(name):
    def decorator(test_fn):
        global passed, failed
        try:
            test_fn()
            print(f"  PASSED: {name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAILED: {name}")
            print(f"     {e}")
            failed += 1
        except Exception as e:
            print(f"  FAILED: {name}")
            print(f"     Unexpected: {type(e).__name__}: {e}")
            failed += 1
    return decorator

def valid_use_case_data(overrides=None):
    """Returns a valid UseCaseCreate payload"""
    data = {
        "title": "Advanced Predictive Maintenance System Implementation",
        "subtitle": "Reducing downtime through AI-powered analytics",
        "description": "We implemented a predictive maintenance system across our entire manufacturing facility. The system uses machine learning algorithms to predict equipment failures 48 hours in advance, allowing preventive maintenance scheduling. This has significantly reduced unplanned downtime and maintenance costs across all production lines. The implementation covered over 200 critical assets.",
        "category": "Predictive Maintenance",
        "factoryName": "IIoT Solutions Factory",
        "city": "Riyadh",
        "latitude": 24.7136,
        "longitude": 46.6753,
        "industryContext": "Our facility operates 24/7 with high-value industrial machinery. Unexpected breakdowns were causing significant production losses. The manufacturing industry context requires high reliability and uptime for all critical production equipment across multiple shifts.",
        "specificProblems": [
            "Frequent unexpected machine breakdowns causing production delays",
            "High maintenance costs due to reactive repair strategies"
        ],
        "financialLoss": "Annual loss of $500,000 due to unplanned downtime",
        "selectionCriteria": [
            "Solution must support Modbus and OPC-UA protocols",
            "Vendor must have proven track record in manufacturing"
        ],
        "selectedVendor": "Siemens Industrial Solutions",
        "technologyComponents": [
            "Edge computing gateways for real-time data collection from sensors",
            "Cloud-based ML platform with automated model retraining pipeline"
        ],
        "implementationTime": "8 months",
        "totalBudget": "$250,000",
        "methodology": "We followed a phased agile methodology with two-week sprints. Phase 1 focused on sensor installation and data collection. Phase 2 involved model training and validation. Phase 3 was production deployment and team training. Each phase had clear KPIs and go/no-go decision gates with stakeholder reviews.",
        "quantitativeResults": [
            {"metric": "Downtime Reduction", "baseline": "120 hrs/month", "current": "24 hrs/month", "improvement": "80%"},
            {"metric": "Cost Savings", "baseline": "$50,000/mo", "current": "$15,000/mo", "improvement": "70%"}
        ],
        "challengesSolutions": [
            {"challenge": "Data quality issues from legacy sensors", "description": "Legacy sensors produced inconsistent data with frequent gaps. We needed reliable data streams for accurate ML predictions across all production lines.", "solution": "Implemented data validation pipeline with anomaly detection. Added redundant sensor arrays at critical points with automatic failover.", "outcome": "Data quality improved to 99.5% with no gaps in critical data streams"}
        ]
    }
    if overrides:
        data.update(overrides)
    return data

def valid_forum_data(overrides=None):
    """Returns a valid ForumPostCreate payload"""
    data = {
        "title": "Best practices for implementing predictive maintenance",
        "content": "I wanted to start a discussion about the best approaches for implementing predictive maintenance in medium-sized manufacturing facilities. We are currently evaluating different solutions and would love to hear from others who have gone through this process. What worked well and what pitfalls should we avoid?",
        "category_id": "Technology Discussion",
        "tags": ["predictive", "maintenance"]
    }
    if overrides:
        data.update(overrides)
    return data


# ============================================================
# 1. DANGEROUS PATTERNS - check_safe_text()
# ============================================================
print("=" * 60)
print("SECTION 1: check_safe_text() - Dangerous Patterns")
print("=" * 60)

@run_test("Blocks <script> tags")
def _(): expect_safe_text_to_reject("<script>alert(1)</script>")

@run_test("Blocks javascript: protocol")
def _(): expect_safe_text_to_reject("javascript:alert(1)")

@run_test("Blocks javascript: with spaces")
def _(): expect_safe_text_to_reject("javascript :alert(1)")

@run_test("Blocks onerror handler")
def _(): expect_safe_text_to_reject("onerror=alert(1)")

@run_test("Blocks onload handler")
def _(): expect_safe_text_to_reject("onload=evil()")

@run_test("Blocks onclick handler")
def _(): expect_safe_text_to_reject("onclick=malicious()")

@run_test("Blocks onmouseover handler")
def _(): expect_safe_text_to_reject("onmouseover=evil()")

@run_test("Blocks onkeydown handler")
def _(): expect_safe_text_to_reject("onkeydown=steal()")

@run_test("Blocks onsubmit handler")
def _(): expect_safe_text_to_reject("onsubmit=phish()")

@run_test("Blocks onfocus handler")
def _(): expect_safe_text_to_reject("onfocus=grab()")

@run_test("Blocks onblur handler")
def _(): expect_safe_text_to_reject("onblur=leak()")

@run_test("Blocks onchange handler")
def _(): expect_safe_text_to_reject("onchange=exfil()")

@run_test("Blocks path traversal ../")
def _(): expect_safe_text_to_reject("../../etc/shadow")

@run_test("Blocks path traversal ..\\\\")
def _(): expect_safe_text_to_reject(r"..\\..\\windows\\system32")

@run_test("Blocks /etc/passwd reference")
def _(): expect_safe_text_to_reject("/etc/passwd")

@run_test("Blocks oastify.com exfiltration")
def _(): expect_safe_text_to_reject("http://malicious.oastify.com/steal")

@run_test("Blocks XXE DOCTYPE probe")
def _(): expect_safe_text_to_reject("<!DOCTYPE foo [")

@run_test("Blocks XInclude probe")
def _(): expect_safe_text_to_reject("<xi:include")

@run_test("Blocks xsi:schemaLocation")
def _(): expect_safe_text_to_reject("xsi:schemaLocation=anything")

@run_test("Blocks SSI <!--#exec probe")
def _(): expect_safe_text_to_reject("<!--#exec cmd=\"ls\"")

@run_test("Blocks LDAP objectClass injection")
def _(): expect_safe_text_to_reject("objectClass=*")

@run_test("Blocks null bytes")
def _(): expect_safe_text_to_reject("malicious\x00payload")

@run_test("Allows normal Arabic text")
def _(): expect_safe_text_to_accept("مرحبا بالعالم هذا نص عادي")

@run_test("Allows normal English text")
def _(): expect_safe_text_to_accept("This is a normal sentence about manufacturing.")

@run_test("Allows URLs with valid protocols")
def _(): expect_safe_text_to_accept("https://example.com/page?q=search")

@run_test("Allows numbers and punctuation")
def _(): expect_safe_text_to_accept("Test 123: (90%) - $500,000 [confirmed]")

# ============================================================
# 2. check_safe_tag() tests
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: check_safe_tag()")
print("=" * 60)

@run_test("Rejects tag too short (< 2 chars)")
def _(): expect_tag_to_reject("a")

@run_test("Rejects tag too long (> 30 chars)")
def _(): expect_tag_to_reject("thisisaverylongtagthatexceeds30chars")

@run_test("Rejects tag with special chars")
def _(): expect_tag_to_reject("tag<script>")

@run_test("Allows valid English tag")
def _(): expect_tag_to_accept("predictive-maintenance")

@run_test("Allows tag with spaces")
def _(): expect_tag_to_accept("predictive maintenance")

# ============================================================
# 3. FORUM POST - Length Constraints
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: ForumPostCreate - Length Constraints")
print("=" * 60)

@run_test("Rejects title < 8 chars")
def _():
    expect_validation_error(ForumPostCreate, {
        "title": "Short",
        "content": "This is a long enough content string to pass the minimum length check for forum posts and more.",
        "category_id": "General"
    })

@run_test("Rejects title > 150 chars")
def _():
    expect_validation_error(ForumPostCreate, {
        "title": "A" * 151,
        "content": "This is a long enough content string to pass the minimum length check for forum posts and more.",
        "category_id": "General"
    })

@run_test("Rejects content < 20 chars")
def _():
    expect_validation_error(ForumPostCreate, {
        "title": "Valid forum post title here",
        "content": "Short content",
        "category_id": "General"
    })

@run_test("Rejects content > 5000 chars")
def _():
    expect_validation_error(ForumPostCreate, {
        "title": "Valid forum post title here",
        "content": "X" * 5001,
        "category_id": "General"
    })

@run_test("Allows valid forum post")
def _():
    expect_schema_ok(ForumPostCreate, valid_forum_data())

# ============================================================
# 4. FORUM POST - XSS in Fields
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: ForumPostCreate - XSS in Fields")
print("=" * 60)

@run_test("XSS in title - <script>")
def _():
    expect_validation_error(ForumPostCreate, valid_forum_data({"title": "Hacked <script>steal()</script>"}))

@run_test("XSS in title - javascript:")
def _():
    expect_validation_error(ForumPostCreate, valid_forum_data({"title": "javascript:alert(1)"}))

@run_test("XSS in title - onerror")
def _():
    expect_validation_error(ForumPostCreate, valid_forum_data({"title": "Image fails <img src=x onerror=alert(1)>"}))

@run_test("XSS in content - <script>")
def _():
    expect_validation_error(ForumPostCreate, valid_forum_data({"content": "<script>document.cookie</script>"}))

@run_test("Tags limit - more than 5")
def _():
    expect_validation_error(ForumPostCreate, valid_forum_data({"tags": ["a", "b", "c", "d", "e", "f"]}))

@run_test("Tags with special characters")
def _():
    expect_validation_error(ForumPostCreate, valid_forum_data({"tags": ["<script>"]}))

# ============================================================
# 5. REPLY CREATE - Validation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: ReplyCreate - Validation")
print("=" * 60)

@run_test("Rejects reply < 2 chars")
def _():
    expect_validation_error(ReplyCreate, {"content": "A"})

@run_test("Rejects reply > 3000 chars")
def _():
    expect_validation_error(ReplyCreate, {"content": "X" * 3001})

@run_test("XSS in reply - <script>")
def _():
    expect_validation_error(ReplyCreate, {"content": "<script>alert(1)</script>"})

@run_test("XSS in reply - onerror")
def _():
    expect_validation_error(ReplyCreate, {"content": "Check this <img src=x onerror=alert(1)> out"})

@run_test("XSS in reply - javascript:")
def _():
    expect_validation_error(ReplyCreate, {"content": "javascript:evil()"})

@run_test("Allows valid reply")
def _():
    expect_schema_ok(ReplyCreate, {"content": "This is a valid reply with enough characters to pass validation."})

# ============================================================
# 6. POST UPDATE - Validation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: PostUpdate - Validation")
print("=" * 60)

@run_test("Updates with XSS in title")
def _():
    expect_validation_error(PostUpdate, {"title": "<script>alert(1)</script>"})

@run_test("Updates with XSS in content")
def _():
    expect_validation_error(PostUpdate, {"content": "<script>document.cookie</script>"})

@run_test("Updates with too many tags")
def _():
    expect_validation_error(PostUpdate, {"tags": ["a", "b", "c", "d", "e", "f"]})

@run_test("Updates with path traversal in title")
def _():
    expect_validation_error(PostUpdate, {"title": "../../etc/shadow"})

@run_test("Allows valid partial update")
def _():
    expect_schema_ok(PostUpdate, {"title": "Updated safe title for forum post here"})

# ============================================================
# 7. USE CASE - Length Constraints
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: UseCaseCreate - Length Constraints")
print("=" * 60)

@run_test("Rejects title < 10 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"title": "Short"}))

@run_test("Rejects title > 100 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"title": "X" * 101}))

@run_test("Rejects subtitle < 10 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"subtitle": "Short"}))

@run_test("Rejects description < 50 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"description": "Too short description."}))

@run_test("Rejects description > 5000 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"description": "X" * 5001}))

@run_test("Rejects factoryName < 2 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"factoryName": "A"}))

@run_test("Rejects city < 2 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"city": "A"}))

@run_test("Rejects industryContext < 50 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"industryContext": "Short context."}))

@run_test("Rejects methodology < 20 chars")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"methodology": "Short"}))

# ============================================================
# 8. USE CASE - List Limits
# ============================================================
print("\n" + "=" * 60)
print("SECTION 8: UseCaseCreate - List Limits")
print("=" * 60)

@run_test("Rejects > 5 specificProblems")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({
        "specificProblems": [f"Problem {i} is long enough to pass validation rule" for i in range(6)]
    }))

@run_test("Rejects < 2 specificProblems")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({
        "specificProblems": ["Only one problem here but need more"]
    }))

@run_test("Rejects > 5 selectionCriteria")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({
        "selectionCriteria": [f"Criteria {i} is long enough to pass validation rule" for i in range(6)]
    }))

@run_test("Rejects < 2 selectionCriteria")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({
        "selectionCriteria": ["Only one"]
    }))

@run_test("Rejects > 15 technologyComponents")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({
        "technologyComponents": [f"Component {i} is exactly twenty characters." for i in range(16)]
    }))

@run_test("Rejects < 1 technologyComponents")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({
        "technologyComponents": []
    }))

# ============================================================
# 9. USE CASE - Numeric Bounds
# ============================================================
print("\n" + "=" * 60)
print("SECTION 9: UseCaseCreate - Numeric Bounds")
print("=" * 60)

@run_test("Rejects latitude > 90")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"latitude": 100}))

@run_test("Rejects latitude < -90")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"latitude": -100}))

@run_test("Rejects longitude > 180")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"longitude": 200}))

@run_test("Rejects longitude < -180")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"longitude": -200}))

@run_test("Allows latitude = 0")
def _():
    expect_schema_ok(UseCaseCreate, valid_use_case_data({"latitude": 0, "longitude": 0}))

# ============================================================
# 10. USE CASE - XSS in All Fields
# ============================================================
print("\n" + "=" * 60)
print("SECTION 10: UseCaseCreate - XSS in Fields")
print("=" * 60)

@run_test("XSS in title - <script>")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"title": "<script>alert(1)</script>"}))

@run_test("XSS in description - javascript:")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"description": "javascript:malicious()"}))

@run_test("XSS in factoryName - onerror")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"factoryName": "<img src=x onerror=steal()>"}))

@run_test("XSS in city - path traversal")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"city": "../../etc"}))

@run_test("XSS in specificProblem - script")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({
        "specificProblems": ["<script>alert(1)</script>", "Second problem is long enough"]
    }))

@run_test("XSS in selectedVendor - javascript:")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"selectedVendor": "javascript:bad()"}))

@run_test("XSS in implementationTime - onload")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"implementationTime": "onload=evil()"}))

@run_test("XSS in contactPerson - script")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"contactPerson": "<script>hack()</script>"}))

# ============================================================
# 11. USE CASE - Category Validation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 11: UseCaseCreate - Category Validation")
print("=" * 60)

valid_categories = [
    "Quality Control", "Predictive Maintenance", "Factory Automation",
    "Artificial Intelligence", "Sustainability", "Process Optimization",
    "Supply Chain", "Innovation & R&D", "Training & Safety", "Energy Efficiency"
]

for cat in valid_categories:
    @run_test(f"Allows category: {cat}")
    def _test(c=cat):
        expect_schema_ok(UseCaseCreate, valid_use_case_data({"category": c}))

@run_test("Rejects invalid category")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"category": "Invalid Category"}))

@run_test("Rejects empty category")
def _():
    expect_validation_error(UseCaseCreate, valid_use_case_data({"category": ""}))

# ============================================================
# 12. USE CASE - QuantitativeResult Validation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 12: QuantitativeResult - Safe Text")
print("=" * 60)

@run_test("XSS in metric field")
def _():
    expect_validation_error(QuantitativeResult, {
        "metric": "<script>alert(1)</script>",
        "baseline": "10 hrs",
        "current": "5 hrs",
        "improvement": "50%"
    })

@run_test("XSS in baseline field")
def _():
    expect_validation_error(QuantitativeResult, {
        "metric": "Downtime",
        "baseline": "javascript:malicious()",
        "current": "5 hrs",
        "improvement": "50%"
    })

# ============================================================
# 13. USE CASE - ChallengeSolution Validation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 13: ChallengeSolution - Safe Text")
print("=" * 60)

@run_test("XSS in challenge field")
def _():
    expect_validation_error(ChallengeSolution, {
        "challenge": "Starts with <script>alert(1)</script> in challenge text",
        "description": "This is a detailed description that is at least twenty characters long.",
        "solution": "This is a detailed solution that is at least twenty characters long.",
        "outcome": "This is an outcome that is long enough to pass."
    })

@run_test("Challenge too short (< 10 chars)")
def _():
    expect_validation_error(ChallengeSolution, {
        "challenge": "Short",
        "description": "This is a detailed description that is at least twenty characters long.",
        "solution": "This is a detailed solution that is at least twenty characters long.",
        "outcome": "This is an outcome that is long enough to pass."
    })

# ============================================================
# 14. USE CASE DRAFT - Validation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 14: UseCaseDraftCreate - Validation")
print("=" * 60)

@run_test("Allows empty draft (all optional)")
def _():
    expect_schema_ok(UseCaseDraftCreate, {})

@run_test("Draft with partial fields works")
def _():
    expect_schema_ok(UseCaseDraftCreate, {"title": "Valid Title Here", "currentStep": 2})

@run_test("Draft rejects XSS in optional title")
def _():
    expect_validation_error(UseCaseDraftCreate, {"title": "<script>alert(1)</script>"})

@run_test("Draft rejects invalid category")
def _():
    expect_validation_error(UseCaseDraftCreate, {"category": "NotAllowed"})

@run_test("Draft allows valid category")
def _():
    expect_schema_ok(UseCaseDraftCreate, {"category": "Quality Control"})

@run_test("Draft rejects latitude > 90")
def _():
    expect_validation_error(UseCaseDraftCreate, {"latitude": 200, "longitude": 46.0})

# ============================================================
# 15. USE CASE UPDATE (Endpoint) - Validation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 15: UseCaseUpdate (Endpoint) - Validation")
print("=" * 60)

@run_test("Update rejects XSS in title")
def _():
    expect_validation_error(EndpointUseCaseUpdate, {"title": "<script>alert(1)</script>"})

@run_test("Update rejects XSS in description")
def _():
    expect_validation_error(EndpointUseCaseUpdate, {"description": "javascript:evil()"})

@run_test("Update rejects invalid category")
def _():
    expect_validation_error(EndpointUseCaseUpdate, {"category": "NotAllowed"})

@run_test("Update rejects latitude > 90")
def _():
    expect_validation_error(EndpointUseCaseUpdate, {"latitude": 100})

@run_test("Update rejects too many tags")
def _():
    expect_validation_error(EndpointUseCaseUpdate, {
        "industryTags": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]
    })

@run_test("Update allows valid partial data")
def _():
    expect_schema_ok(EndpointUseCaseUpdate, {"title": "Valid Updated Title Here"})

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)

if failed > 0:
    print("WARNING: Some tests FAILED. Review the failures above.")
else:
    print("All tests PASSED! Validation is working correctly.")
