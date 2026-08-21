import re

class JobDescriptionParser:
    def __init__(self, jd_text):
        self.jd_text = jd_text

    def extract_role(self):
        # Looks for common patterns like "Role:", "Position:", or extracts first line
        match = re.search(r'(?:role|position|title)[:\s]+([^\n]+)', self.jd_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        lines = [line.strip() for line in self.jd_text.split('\n') if line.strip()]
        return lines[0] if lines else "Unknown Role"

    def extract_skills_required(self, predefined_skills):
        required_skills = []
        for skill in predefined_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', self.jd_text, re.IGNORECASE):
                required_skills.append(skill)
        return required_skills

    def parse(self):
        skill_set = ['Python', 'Java', 'SQL', 'Pandas', 'Machine Learning', 'HTML', 'CSS', 'Git', 'FastAPI']
        return {
            "job_title": self.extract_role(),
            "required_skills": self.extract_skills_required(skill_set)
        }

# Example usage:
if __name__ == "__main__":
    sample_jd = """
    Position: Machine Learning Engineer
    We are looking for a candidate skilled in Python, SQL, and Machine Learning. 
    Experience with FastAPI is a big plus.
    """
    parser = JobDescriptionParser(sample_jd)
    print("Parsed Job Description:", parser.parse())
