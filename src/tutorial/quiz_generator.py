"""
Quiz Generator - Generates quiz questions from documentation.
Part of Feature 5: Interactive Tutorial Generator
"""

import os
import random
from typing import Dict, List, Optional, Any

from src.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class QuizGenerator:
    """
    Generates quiz questions from documentation steps.
    Uses AI for intelligent question generation.
    """
    
    # Predefined question templates
    TEMPLATES = {
        "click": [
            "Was ist der nächste Schritt nach dieser Aktion?",
            "Welches Element sollte angeklickt werden?",
            "Wo befindet sich diese Schaltfläche?"
        ],
        "input": [
            "Welche Art von Daten sollte hier eingegeben werden?",
            "Was passiert nach der Eingabe?",
            "Welches Format wird für diese Eingabe erwartet?"
        ],
        "select": [
            "Welche Option sollte ausgewählt werden?",
            "Warum ist diese Auswahl wichtig?",
            "Was bewirkt diese Auswahl?"
        ]
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_ai: bool = True,
        language: str = "de"
    ):
        """
        Initialize quiz generator.
        
        Args:
            api_key: OpenAI API key
            use_ai: Whether to use AI for generation
            language: Output language
        """
        self.use_ai = use_ai and OPENAI_AVAILABLE
        self.language = language
        
        if self.use_ai:
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
            else:
                self.use_ai = False
        
        logger.info(f"QuizGenerator initialized (AI: {self.use_ai})")
    
    def generate_quiz_for_step(
        self,
        step: Dict[str, Any],
        difficulty: str = "medium"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate quiz question for a step.
        
        Args:
            step: Step data
            difficulty: Question difficulty
            
        Returns:
            Quiz data dictionary or None
        """
        if self.use_ai:
            return self._generate_ai_quiz(step, difficulty)
        else:
            return self._generate_template_quiz(step)
    
    def generate_quiz_for_tutorial(
        self,
        steps: List[Dict[str, Any]],
        questions_per_section: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Generate quizzes for entire tutorial.
        
        Args:
            steps: All tutorial steps
            questions_per_section: Questions per section
            
        Returns:
            List of quiz data dictionaries
        """
        quizzes = []
        
        # Group steps into sections
        section_size = max(3, len(steps) // 5)
        
        for i in range(0, len(steps), section_size):
            section = steps[i:i + section_size]
            
            # Pick random step for quiz
            quiz_step = random.choice(section)
            quiz = self.generate_quiz_for_step(quiz_step)
            
            if quiz:
                quiz["section"] = i // section_size + 1
                quizzes.append(quiz)
        
        return quizzes
    
    def _generate_ai_quiz(
        self,
        step: Dict[str, Any],
        difficulty: str
    ) -> Optional[Dict[str, Any]]:
        """Generate quiz using AI."""
        prompt = f"""Erstelle eine Quiz-Frage für den folgenden Dokumentationsschritt.
Schwierigkeit: {difficulty}

Schritt: {step.get('description', '')}
Fenster: {step.get('window_title', '')}

Erstelle:
1. Eine präzise Frage
2. 4 Antwortoptionen (eine korrekt)
3. Die Nummer der korrekten Antwort (0-3)

Antworte im Format:
FRAGE: [Frage]
A: [Antwort 1]
B: [Antwort 2]
C: [Antwort 3]
D: [Antwort 4]
KORREKT: [0-3]"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            text = response.choices[0].message.content
            return self._parse_ai_response(text)
        
        except Exception as e:
            logger.warning(f"AI quiz generation failed: {e}")
            return self._generate_template_quiz(step)
    
    def _generate_template_quiz(
        self,
        step: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate quiz from templates."""
        desc = step.get("description", "").lower()
        
        # Determine action type
        if any(w in desc for w in ["click", "klick"]):
            action_type = "click"
        elif any(w in desc for w in ["enter", "type", "eingeb"]):
            action_type = "input"
        elif any(w in desc for w in ["select", "wähl"]):
            action_type = "select"
        else:
            return None
        
        # Get random question template
        questions = self.TEMPLATES.get(action_type, [])
        if not questions:
            return None
        
        question = random.choice(questions)
        
        # Generate generic answers
        answers = [
            step.get("description", "Die beschriebene Aktion")[:50],
            "Eine andere Aktion",
            "Abbrechen",
            "Zurück zum Start"
        ]
        random.shuffle(answers[1:])
        answers = [answers[0]] + answers[1:]
        
        return {
            "question": question,
            "answers": answers,
            "correct": 0,
            "explanation": f"Siehe Schritt: {step.get('title', 'diesen Schritt')}"
        }
    
    def _parse_ai_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse AI response into quiz format."""
        lines = text.strip().split("\n")
        
        question = ""
        answers = []
        correct = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith("FRAGE:"):
                question = line.replace("FRAGE:", "").strip()
            elif line.startswith(("A:", "B:", "C:", "D:")):
                answers.append(line[2:].strip())
            elif line.startswith("KORREKT:"):
                try:
                    correct = int(line.replace("KORREKT:", "").strip())
                except:
                    correct = 0
        
        if question and len(answers) >= 2:
            return {
                "question": question,
                "answers": answers,
                "correct": correct
            }
        
        return None

