import os
import json
import jmespath
from typing import List, Dict, Any, Callable

RULE_PACKS_DIR = os.path.join(os.path.dirname(__file__), '..', 'rule_packs')

class Rule:
    def __init__(self, rule_id: str, description: str, severity: str, test: str, test_type: str = 'jmespath'):
        self.id = rule_id
        self.description = description
        self.severity = severity
        self.test = test
        self.test_type = test_type  # 'jmespath' or 'python'

    def evaluate(self, scan_result: dict) -> bool:
        if self.test_type == 'jmespath':
            return bool(jmespath.search(self.test, scan_result))
        elif self.test_type == 'python':
            # WARNING: eval is dangerous; in production, use a safe sandbox
            try:
                return bool(eval(self.test, {}, {'result': scan_result}))
            except Exception:
                return False
        else:
            raise ValueError(f"Unknown test_type: {self.test_type}")

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'severity': self.severity,
            'test': self.test,
            'test_type': self.test_type
        }

def load_rules() -> List[Rule]:
    rules = []
    for fname in os.listdir(RULE_PACKS_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(RULE_PACKS_DIR, fname), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for rule in data.get('rules', []):
                    rules.append(Rule(
                        rule_id=rule['id'],
                        description=rule.get('description', ''),
                        severity=rule.get('severity', 'medium'),
                        test=rule['test'],
                        test_type=rule.get('test_type', 'jmespath')
                    ))
    return rules

def evaluate_rules(scan_result: dict, rules: List[Rule]) -> List[Dict[str, Any]]:
    violations = []
    for rule in rules:
        if rule.evaluate(scan_result):
            violations.append({
                'id': rule.id,
                'description': rule.description,
                'severity': rule.severity
            })
    return violations

# Example usage
if __name__ == "__main__":
    # Example scan result
    scan_result = {
        "cookie_banner_detected": False,
        "cookies": [],
        "url": "https://example.com"
    }
    # Example rule (would normally be in a JSON file)
    example_rule = Rule(
        rule_id="missing_cookie_banner",
        description="No cookie banner detected on the page",
        severity="high",
        test="!cookie_banner_detected",
        test_type="python"
    )
    violations = evaluate_rules(scan_result, [example_rule])
    print(json.dumps(violations, indent=2)) 