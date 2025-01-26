from zapv2 import ZAPv2

# Test for SQL injection vulnerabilities
def test_sql_injection():
    zap = ZAPv2()
    target = "http://localhost:5000"
    zap.urlopen(target)
    zap.spider.scan(target)
    zap.active_scan.scan(target)
    alerts = zap.core.alerts()
    assert len(alerts) == 0, "Security vulnerabilities found!"

# Test for XSS vulnerabilities
def test_xss():
    zap = ZAPv2()
    target = "http://localhost:5000"
    zap.urlopen(target)
    zap.spider.scan(target)
    zap.active_scan.scan(target)
    alerts = zap.core.alerts()
    assert len(alerts) == 0, "XSS vulnerabilities found!"