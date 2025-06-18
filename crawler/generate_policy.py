import os

def generate_policy(lang: str, company_name: str, contact_email: str) -> str:
    template_path = os.path.join(os.path.dirname(__file__), f'../policy_templates/{lang}.md')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    return template.replace('{{company_name}}', company_name).replace('{{contact_email}}', contact_email)

if __name__ == "__main__":
    # Example usage
    print(generate_policy('en', 'RegulaAI', 'privacy@regulaai.com')) 