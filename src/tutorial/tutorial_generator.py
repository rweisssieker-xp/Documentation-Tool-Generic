"""
Tutorial Generator - Creates interactive tutorials from documentation.
Part of Feature 5: Interactive Tutorial Generator
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TutorialStep:
    """A step in the tutorial."""
    id: str
    title: str
    content: str
    screenshot: Optional[str]
    quiz_question: Optional[str] = None
    quiz_answers: List[str] = field(default_factory=list)
    correct_answer: int = 0
    hints: List[str] = field(default_factory=list)
    duration_estimate: int = 60  # seconds


@dataclass
class Tutorial:
    """A complete interactive tutorial."""
    id: str
    title: str
    description: str
    steps: List[TutorialStep]
    prerequisites: List[str]
    learning_objectives: List[str]
    difficulty: str
    estimated_duration: int
    tags: List[str]


class TutorialGenerator:
    """
    Generates interactive tutorials from documentation sessions.
    """
    
    def __init__(
        self,
        quiz_generator: Optional[Any] = None,
        include_quizzes: bool = True
    ):
        """
        Initialize tutorial generator.
        
        Args:
            quiz_generator: QuizGenerator instance
            include_quizzes: Whether to include quiz questions
        """
        self.quiz_generator = quiz_generator
        self.include_quizzes = include_quizzes
        
        logger.info("TutorialGenerator initialized")
    
    def generate_tutorial(
        self,
        session_data: Dict[str, Any],
        title: Optional[str] = None
    ) -> Tutorial:
        """
        Generate interactive tutorial from session.
        
        Args:
            session_data: Session data
            title: Tutorial title
            
        Returns:
            Tutorial object
        """
        steps = session_data.get("steps", [])
        
        tutorial_steps = []
        for i, step in enumerate(steps):
            tutorial_step = self._create_tutorial_step(step, i + 1)
            tutorial_steps.append(tutorial_step)
        
        # Generate learning objectives
        objectives = self._generate_learning_objectives(steps)
        
        # Calculate duration
        duration = sum(s.duration_estimate for s in tutorial_steps)
        
        tutorial = Tutorial(
            id=f"tutorial_{session_data.get('session_id', 'unknown')[:8]}",
            title=title or session_data.get("name", "Interactive Tutorial"),
            description=session_data.get("description", "Learn this workflow step by step"),
            steps=tutorial_steps,
            prerequisites=self._extract_prerequisites(steps),
            learning_objectives=objectives,
            difficulty=self._estimate_difficulty(steps),
            estimated_duration=duration,
            tags=["generated", session_data.get("application", "")]
        )
        
        logger.info(f"Generated tutorial: {tutorial.title} ({len(tutorial_steps)} steps)")
        return tutorial
    
    def export_html(
        self,
        tutorial: Tutorial,
        output_path: str,
        include_navigation: bool = True
    ) -> str:
        """
        Export tutorial as interactive HTML.
        
        Args:
            tutorial: Tutorial to export
            output_path: Output file path
            include_navigation: Include step navigation
            
        Returns:
            HTML content
        """
        html = self._generate_html(tutorial, include_navigation)
        Path(output_path).write_text(html, encoding='utf-8')
        logger.info(f"Exported HTML tutorial to: {output_path}")
        return html
    
    def _create_tutorial_step(
        self,
        step: Dict[str, Any],
        step_number: int
    ) -> TutorialStep:
        """Create a tutorial step from documentation step."""
        # Generate quiz if enabled
        quiz_question = None
        quiz_answers = []
        correct_answer = 0
        
        if self.include_quizzes and self.quiz_generator:
            quiz_data = self.quiz_generator.generate_quiz_for_step(step)
            if quiz_data:
                quiz_question = quiz_data.get("question")
                quiz_answers = quiz_data.get("answers", [])
                correct_answer = quiz_data.get("correct", 0)
        
        # Generate hints
        hints = self._generate_hints(step)
        
        return TutorialStep(
            id=f"step_{step_number}",
            title=step.get("title", f"Schritt {step_number}"),
            content=step.get("description", ""),
            screenshot=step.get("screenshot"),
            quiz_question=quiz_question,
            quiz_answers=quiz_answers,
            correct_answer=correct_answer,
            hints=hints,
            duration_estimate=self._estimate_step_duration(step)
        )
    
    def _generate_hints(self, step: Dict[str, Any]) -> List[str]:
        """Generate hints for a step."""
        hints = []
        
        desc = step.get("description", "").lower()
        
        if "click" in desc or "klick" in desc:
            hints.append("Achten Sie auf die hervorgehobene Schaltfläche im Screenshot")
        
        if "enter" in desc or "eingeb" in desc:
            hints.append("Überprüfen Sie die Eingabe vor dem Bestätigen")
        
        if step.get("window_title"):
            hints.append(f"Sie sollten sich im Fenster '{step['window_title']}' befinden")
        
        return hints
    
    def _estimate_step_duration(self, step: Dict[str, Any]) -> int:
        """Estimate step duration in seconds."""
        base_duration = 30
        
        desc = step.get("description", "")
        
        # Longer for input steps
        if any(w in desc.lower() for w in ["enter", "type", "eingeben", "ausfüllen"]):
            base_duration += 30
        
        # Longer for steps with quiz
        if step.get("quiz"):
            base_duration += 60
        
        return base_duration
    
    def _generate_learning_objectives(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate learning objectives from steps."""
        objectives = []
        
        # Count action types
        actions = {
            "navigation": 0,
            "data_entry": 0,
            "configuration": 0
        }
        
        for step in steps:
            desc = step.get("description", "").lower()
            if any(w in desc for w in ["click", "open", "navigate", "klick", "öffn"]):
                actions["navigation"] += 1
            if any(w in desc for w in ["enter", "type", "input", "eingeb"]):
                actions["data_entry"] += 1
            if any(w in desc for w in ["setting", "config", "option", "einstell"]):
                actions["configuration"] += 1
        
        if actions["navigation"] > 0:
            objectives.append("Die Navigation durch die Anwendung verstehen")
        if actions["data_entry"] > 0:
            objectives.append("Dateneingabe korrekt durchführen")
        if actions["configuration"] > 0:
            objectives.append("Wichtige Einstellungen konfigurieren")
        
        objectives.append("Den gesamten Workflow selbstständig durchführen können")
        
        return objectives
    
    def _extract_prerequisites(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Extract prerequisites from steps."""
        prerequisites = []
        
        if steps:
            first = steps[0]
            if first.get("window_title"):
                prerequisites.append(f"Zugang zu: {first['window_title']}")
            
            app = first.get("application")
            if app:
                prerequisites.append(f"{app} ist installiert und gestartet")
        
        prerequisites.append("Grundlegende Computerkenntnisse")
        
        return prerequisites
    
    def _estimate_difficulty(self, steps: List[Dict[str, Any]]) -> str:
        """Estimate tutorial difficulty."""
        if len(steps) <= 5:
            return "Anfänger"
        elif len(steps) <= 15:
            return "Fortgeschritten"
        else:
            return "Experte"
    
    def _generate_html(
        self,
        tutorial: Tutorial,
        include_navigation: bool
    ) -> str:
        """Generate interactive HTML for tutorial."""
        html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tutorial.title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', sans-serif; line-height: 1.6; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .meta {{ display: flex; gap: 20px; flex-wrap: wrap; margin-top: 20px; font-size: 0.9em; opacity: 0.9; }}
        .meta-item {{ display: flex; align-items: center; gap: 5px; }}
        .step {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .step-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .step-number {{ background: #667eea; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }}
        .step-content {{ margin: 20px 0; }}
        .screenshot {{ max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin: 20px 0; }}
        .quiz {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .quiz-question {{ font-weight: 600; margin-bottom: 15px; }}
        .quiz-answer {{ padding: 10px 15px; margin: 5px 0; background: white; border: 2px solid #e0e0e0; border-radius: 6px; cursor: pointer; transition: all 0.2s; }}
        .quiz-answer:hover {{ border-color: #667eea; }}
        .quiz-answer.correct {{ background: #d4edda; border-color: #28a745; }}
        .quiz-answer.incorrect {{ background: #f8d7da; border-color: #dc3545; }}
        .hint {{ background: #fff3cd; padding: 15px; border-radius: 6px; margin-top: 15px; border-left: 4px solid #ffc107; }}
        .navigation {{ display: flex; justify-content: space-between; margin-top: 30px; }}
        .btn {{ padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; transition: all 0.2s; }}
        .btn-primary {{ background: #667eea; color: white; }}
        .btn-primary:hover {{ background: #5a6fd6; }}
        .progress {{ background: #e0e0e0; height: 6px; border-radius: 3px; margin-bottom: 30px; }}
        .progress-bar {{ background: #667eea; height: 100%; border-radius: 3px; transition: width 0.3s; }}
        .objectives {{ background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .objectives h3 {{ color: #0066cc; margin-bottom: 10px; }}
        .objectives ul {{ margin-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{tutorial.title}</h1>
            <p>{tutorial.description}</p>
            <div class="meta">
                <span class="meta-item">⏱️ {tutorial.estimated_duration // 60} Min.</span>
                <span class="meta-item">📊 {tutorial.difficulty}</span>
                <span class="meta-item">📝 {len(tutorial.steps)} Schritte</span>
            </div>
        </header>

        <div class="progress">
            <div class="progress-bar" id="progress" style="width: 0%"></div>
        </div>

        <div class="objectives">
            <h3>🎯 Lernziele</h3>
            <ul>
                {"".join(f"<li>{obj}</li>" for obj in tutorial.learning_objectives)}
            </ul>
        </div>
'''
        
        for i, step in enumerate(tutorial.steps):
            html += f'''
        <div class="step" id="step-{i+1}" {"style='display:none;'" if i > 0 else ""}>
            <div class="step-header">
                <div class="step-number">{i+1}</div>
                <h2>{step.title}</h2>
            </div>
            <div class="step-content">
                <p>{step.content}</p>
                {"<img class='screenshot' src='" + step.screenshot + "' alt='Screenshot'>" if step.screenshot else ""}
            </div>
'''
            
            if step.quiz_question:
                html += f'''
            <div class="quiz">
                <p class="quiz-question">❓ {step.quiz_question}</p>
                {"".join(f'<div class="quiz-answer" onclick="checkAnswer(this, {step.correct_answer}, {j})">{ans}</div>' for j, ans in enumerate(step.quiz_answers))}
            </div>
'''
            
            if step.hints:
                html += f'''
            <div class="hint">
                💡 <strong>Tipp:</strong> {step.hints[0]}
            </div>
'''
            
            if include_navigation:
                html += f'''
            <div class="navigation">
                {"<button class='btn' onclick='prevStep({i+1})'>← Zurück</button>" if i > 0 else "<div></div>"}
                {"<button class='btn btn-primary' onclick='nextStep({i+1})'>Weiter →</button>" if i < len(tutorial.steps)-1 else "<button class='btn btn-primary' onclick='complete()'>Abschließen ✓</button>"}
            </div>
'''
            
            html += '</div>\n'
        
        html += '''
    </div>

    <script>
        let currentStep = 1;
        const totalSteps = ''' + str(len(tutorial.steps)) + ''';

        function updateProgress() {
            const progress = (currentStep / totalSteps) * 100;
            document.getElementById('progress').style.width = progress + '%';
        }

        function showStep(n) {
            for (let i = 1; i <= totalSteps; i++) {
                document.getElementById('step-' + i).style.display = i === n ? 'block' : 'none';
            }
            currentStep = n;
            updateProgress();
        }

        function nextStep(current) {
            if (current < totalSteps) showStep(current + 1);
        }

        function prevStep(current) {
            if (current > 1) showStep(current - 1);
        }

        function checkAnswer(element, correct, selected) {
            const answers = element.parentElement.querySelectorAll('.quiz-answer');
            answers.forEach((ans, i) => {
                ans.classList.remove('correct', 'incorrect');
                if (i === correct) ans.classList.add('correct');
                else if (i === selected && selected !== correct) ans.classList.add('incorrect');
            });
        }

        function complete() {
            alert('🎉 Herzlichen Glückwunsch! Sie haben das Tutorial abgeschlossen.');
        }

        updateProgress();
    </script>
</body>
</html>'''
        
        return html

