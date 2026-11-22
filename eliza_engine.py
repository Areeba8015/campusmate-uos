import json
import random
import re
import time


class ElizaEngine:
    """Symbolic AI engine implementing ELIZA keyword ranking, reflection, and memory."""

    def __init__(self, rules_path: str = "rules.json"):
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.reflections = data.get("reflections", {})
        # Sort rules by priority (highest first)
        self.rules = sorted(
            data.get("rules", []),
            key=lambda x: x.get("priority", 0),
            reverse=True,
        )
        self.memory_stack = []

    def reflect(self, fragment: str) -> str:
        """Swaps first-person pronouns to second-person (classic ELIZA transformation)."""
        words = fragment.lower().split()
        reflected_words = [self.reflections.get(word, word) for word in words]
        return " ".join(reflected_words)

    def fill_template(self, template: str, groups: tuple) -> str:
        """Replaces {1}, {2}, etc. with reflected regex capture groups."""
        result = template
        for idx, group in enumerate(groups, start=1):
            if group:
                result = result.replace(f"{{{idx}}}", self.reflect(group))
        return result

    def get_response(self, user_input: str) -> tuple[str, dict]:
        """Matches input against ranked regex rules and manages the memory stack."""
        start_time = time.perf_counter()
        cleaned_input = re.sub(r"[^\w\s\.\-\?]", "", user_input.strip())

        for rule in self.rules:
            for pattern in rule["patterns"]:
                match = re.search(pattern, cleaned_input, re.IGNORECASE)
                if match:
                    intent = rule["intent"]

                    # Pop from ELIZA memory stack when hitting FALLBACK
                    if intent == "FALLBACK" and self.memory_stack:
                        recalled_response = self.memory_stack.pop(0)
                        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                        debug_info = {
                            "intent": "FALLBACK_MEMORY_RECALL",
                            "priority": rule["priority"],
                            "matched_pattern": "MEMORY_QUEUE_POP",
                            "latency_ms": latency_ms,
                        }
                        return recalled_response, debug_info

                    # Generate standard rule response
                    template = random.choice(rule["responses"])
                    response = self.fill_template(template, match.groups())

                    # Push follow-up question onto memory stack if defined
                    if rule.get("memory_templates"):
                        mem_template = random.choice(rule["memory_templates"])
                        mem_sentence = self.fill_template(mem_template, match.groups())
                        if mem_sentence not in self.memory_stack:
                            self.memory_stack.append(mem_sentence)

                    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    debug_info = {
                        "intent": intent,
                        "priority": rule["priority"],
                        "matched_pattern": pattern,
                        "latency_ms": latency_ms,
                    }
                    return response, debug_info

        return "I'm not sure how to respond to that.", {}

    def clear_memory(self):
        """Resets ELIZA's saved memory stack."""
        self.memory_stack.clear()
