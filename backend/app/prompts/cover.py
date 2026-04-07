"""Cover letter generation prompts."""

COVER_LETTER_SYSTEM = """You write concise, professional cover letters in Russian as Markdown.
Output only the letter body (no subject line), tailored to the vacancy. No JSON."""

COVER_LETTER_USER_TEMPLATE = """Vacancy:\nTitle: {title}\nCompany: {company}\nRequirements summary:\n{requirements}\n\nCandidate resume (markdown):\n{resume}\n"""
