import re

class PromptInjectionDetector:
    PATTERNS = [
    #1. system Ovveride
    (r"(?i)(ignore|disregard|forget|override|bypass|disable|circumvent|neglect|omit|skip|avoid|suppress|remove|delete|erase|conceal|hide|mask|obscure|camouflage|cloak)\s+(the\s+)?(system\s+)?(instructions?|rules?|guidelines?|policies?|restrictions?|limitations?|boundaries?|constraints?)",
    "System Override: Attempt to bypass or disable system instructions or rules."),
    #2. Roleplaying
    (r"(?i)(act as|pretend to be|roleplay as|assume the role of|take on the persona of|imitate|emulate|mimic|simulate|play the part of|become)\s+(a\s+)?([\w\s]+)?(character|persona|role|identity|agent|entity|bot|assistant|model|AI|chatbot|virtual assistant|digital assistant|language model|hacker|person|individual|user|someone|something)?",
    "Roleplaying: Attempt to assume a different identity or role to bypass restrictions."),
    #3. Output Manipulation
    (r"(?i)(generate|create|produce|output|provide|give|write|compose|formulate|construct|craft|develop|design|build|assemble|fabricate|invent|devise|engineer|synthesize|simulate|mimic|emulate|imitate|replicate|reproduce|forge|counterfeit|falsify|manipulate|alter|modify|change|transform|convert|circumvent|bypass|disable|evade|avoid|suppress|conceal|hide|mask|obscure|camouflage|cloak)\s+(content|responses?|answers?|output|results?|information|data|text|messages?|replies?|completions?|tokens?)\s*(that\s+)?(bypass|evade|avoid|suppress|conceal|hide|mask|obscure|camouflage|cloak|circumvent|disable|neglect|omit|skip|evade|avoid|suppress|conceal|hide|mask|obscure|camouflage|cloak|override|disregard|ignore|forget|bypass|disable|circumvent|neglect|omit|skip|avoid|suppress|conceal|hide|mask|obscure|camouflage|cloak|break|violate|circumvent|bypass|disable|evade|avoid|suppress|conceal|hide|mask|obscure|camouflage|cloak|rules?|restrictions?|limitations?| boundaries?|constraints?)",
    "Output Manipulation: Attempt to generate content that bypasses restrictions or guidelines."),
    #4. Prompt Injection
    (r"(?i)(insert|embed|include|inject|smuggle|hide|conceal|camouflage|cloak|obscure|mask)\s+(malicious\s+)?(prompts?|instructions?|payloads?|code|commands|scripts?|data|information|content|messages?|text|tokens?)",
    "Prompt Injection: Attempt to insert malicious prompts or instructions to manipulate the model's behavior."),  
    
    #5. Jailbreak
    (r"(?i)(jailbreak|escape|break out|bypass|disable|evade|avoid|suppress|conceal|hide|mask|obscure|camouflage|cloak)\s+(the\s+)?(model|AI|chatbot|assistant|language model|system|restrictions?|limitations?|rules?|guidelines?|policies?)",
    "Jailbreak: Attempt to bypass or disable model restrictions or limitations."),
    
    #6. Prompt Extraction
    (r"(?i)(extract|steal|harvest|scrape|gather|collect|obtain|access|retrieve|leak|exfiltrate|expose|reveal|disclose|uncover|discover|find|access|obtain|steal|harvest|scrape|gather|collect|obtain|access|retrieve|leak|exfiltrate|expose|reveal|disclose|uncover|discover|find)\s+(sensitive\s+)?(prompts?|instructions?|payloads?|code|commands|scripts?|data|information|content|messages?|text|tokens?)",
    "Prompt Extraction: Attempt to extract sensitive prompts or instructions from the model."),
    ]
    
    def __init__(self,max_length= 4000):
        # Initialize any necessary data structures or configurations
        self.max_length = max_length
        self.compiled_patterns = [
            (re.compile(pattern), description) for pattern, description in self.PATTERNS
        ]    
    
    
    def detect(self, user_input: str) -> tuple[bool, list[str]]:
        if not user_input:
            return False, []
        response = []
        if len(user_input) > self.max_length:
            response.append(f"Input exceeds maximum length of {self.max_length} characters.")
        response.extend([reason for pattern, reason in self.compiled_patterns if pattern.search(user_input)])
        return bool(response), response