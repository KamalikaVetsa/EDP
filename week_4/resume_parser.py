import re

class ResumeParser:
    def __init__(self, text):
        self.text = text

    def extract_email(self):
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', self.text)
        return match.group(0) if match else None

    def extract_phone(self):
        # Matches standard international and local phone patterns
        match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', self.text)
        return match.group(0) if match else None

    def extract_skills(self, predefined_skills):
        found_skills = []
        for skill in predefined_skills:
            # Case-insensitive search for skills
            if re.search(r'\b' + re.escape(skill) + r'\b', self.text, re.IGNORECASE):
                found_skills.append(skill)
        return found_skills

    def parse(self):
        # Common skill keywords to look for in resumes
        skill_set = ['Python', 'Java', 'SQL', 'Pandas', 'Machine Learning', 'HTML', 'CSS', 'Git', 'FastAPI']
        
        return {
            "email": self.extract_email(),
            "phone": self.extract_phone(),
            "skills": self.extract_skills(skill_set)
        }

# Example usage:
if __name__ == "__main__":
    sample_resume = """
    John Doe
    Email: john.doe@email.com, Phone: +1-555-019-2834
    Skills: Proficient in Python, SQL, and Machine Learning basics. Experience with Git.
    """
    parser = ResumeParser(sample_resume)
    print("Parsed Resume Data:", parser.parse())
