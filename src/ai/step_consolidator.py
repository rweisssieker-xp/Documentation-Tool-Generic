"""
Intelligente Schritt-Konsolidierung: Erkennt ähnliche Schritte und schlägt Konsolidierung vor
"""

import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from PIL import Image
import numpy as np

from src.ai.openai_client import OpenAIClient
from src.capture.ocr_engine import OCREngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StepConsolidator:
    """Erkennt ähnliche Schritte und schlägt Konsolidierung vor"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialisiert den Step Consolidator
        
        Args:
            similarity_threshold: Schwellenwert für Ähnlichkeit (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.openai_client = OpenAIClient()
        self.ocr_engine = OCREngine()
    
    def find_similar_steps(self, steps: List[Dict]) -> List[Dict[str, any]]:
        """
        Findet ähnliche Schritte
        
        Args:
            steps: Liste von Schritt-Dictionaries
            
        Returns:
            Liste von Konsolidierungs-Vorschlägen
        """
        suggestions = []
        
        if len(steps) < 2:
            return suggestions
        
        # Vergleiche alle Schritte paarweise
        for i in range(len(steps)):
            for j in range(i + 1, len(steps)):
                similarity = self._calculate_similarity(steps[i], steps[j])
                
                if similarity >= self.similarity_threshold:
                    suggestions.append({
                        'step1_index': i,
                        'step2_index': j,
                        'step1': steps[i],
                        'step2': steps[j],
                        'similarity': similarity,
                        'reason': self._get_similarity_reason(steps[i], steps[j])
                    })
        
        # Sortiere nach Ähnlichkeit (höchste zuerst)
        suggestions.sort(key=lambda x: x['similarity'], reverse=True)
        
        return suggestions
    
    def _calculate_similarity(self, step1: Dict, step2: Dict) -> float:
        """
        Berechnet Ähnlichkeit zwischen zwei Schritten
        
        Args:
            step1: Erster Schritt
            step2: Zweiter Schritt
            
        Returns:
            Ähnlichkeitswert (0.0-1.0)
        """
        similarity_scores = []
        
        # 1. Fenster-Titel-Ähnlichkeit
        title1 = step1.get('window_title', '')
        title2 = step2.get('window_title', '')
        if title1 and title2:
            title_sim = self._string_similarity(title1, title2)
            similarity_scores.append(title_sim * 0.3)  # 30% Gewichtung
        
        # 2. OCR-Text-Ähnlichkeit
        ocr_sim = self._ocr_text_similarity(step1, step2)
        if ocr_sim is not None:
            similarity_scores.append(ocr_sim * 0.4)  # 40% Gewichtung
        
        # 3. Screenshot-Ähnlichkeit
        screenshot_sim = self._screenshot_similarity(step1, step2)
        if screenshot_sim is not None:
            similarity_scores.append(screenshot_sim * 0.3)  # 30% Gewichtung
        
        # Gewichteter Durchschnitt
        if similarity_scores:
            return sum(similarity_scores) / len(similarity_scores)
        
        return 0.0
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Berechnet String-Ähnlichkeit (Jaccard-Ähnlichkeit)"""
        if not str1 or not str2:
            return 0.0
        
        set1 = set(str1.lower().split())
        set2 = set(str2.lower().split())
        
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _ocr_text_similarity(self, step1: Dict, step2: Dict) -> Optional[float]:
        """Berechnet OCR-Text-Ähnlichkeit"""
        try:
            screenshot1 = Path(step1.get('screenshot_path', ''))
            screenshot2 = Path(step2.get('screenshot_path', ''))
            
            if not screenshot1.exists() or not screenshot2.exists():
                return None
            
            if not self.ocr_engine.is_available():
                return None
            
            ocr_text1 = self.ocr_engine.extract_text(screenshot1)
            ocr_text2 = self.ocr_engine.extract_text(screenshot2)
            
            if not ocr_text1 or not ocr_text2:
                return None
            
            return self._string_similarity(ocr_text1, ocr_text2)
        
        except Exception as e:
            logger.warning(f"Fehler bei OCR-Text-Ähnlichkeit: {e}")
            return None
    
    def _screenshot_similarity(self, step1: Dict, step2: Dict) -> Optional[float]:
        """Berechnet Screenshot-Ähnlichkeit basierend auf Hash"""
        try:
            screenshot1 = Path(step1.get('screenshot_path', ''))
            screenshot2 = Path(step2.get('screenshot_path', ''))
            
            if not screenshot1.exists() or not screenshot2.exists():
                return None
            
            # Verwende Perceptual Hash für Ähnlichkeitsprüfung
            hash1 = self._calculate_image_hash(screenshot1)
            hash2 = self._calculate_image_hash(screenshot2)
            
            if hash1 is None or hash2 is None:
                return None
            
            # Hamming-Distanz zwischen Hashes
            hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            similarity = 1.0 - (hamming_distance / len(hash1))
            
            return similarity
        
        except Exception as e:
            logger.warning(f"Fehler bei Screenshot-Ähnlichkeit: {e}")
            return None
    
    def _calculate_image_hash(self, image_path: Path, hash_size: int = 8) -> Optional[str]:
        """Berechnet Perceptual Hash für Bild"""
        try:
            img = Image.open(image_path)
            
            # Konvertiere zu Graustufen und verkleinere
            img = img.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
            
            # Berechne Differenzen
            pixels = list(img.getdata())
            diff = []
            for row in range(hash_size):
                for col in range(hash_size):
                    pixel_left = pixels[row * (hash_size + 1) + col]
                    pixel_right = pixels[row * (hash_size + 1) + col + 1]
                    diff.append(pixel_left > pixel_right)
            
            # Konvertiere zu String
            hash_str = ''.join(['1' if d else '0' for d in diff])
            return hash_str
        
        except Exception as e:
            logger.warning(f"Fehler beim Berechnen des Image-Hash: {e}")
            return None
    
    def _get_similarity_reason(self, step1: Dict, step2: Dict) -> str:
        """Gibt Grund für Ähnlichkeit zurück"""
        reasons = []
        
        title1 = step1.get('window_title', '')
        title2 = step2.get('window_title', '')
        
        if title1 == title2:
            reasons.append("Gleicher Fenster-Titel")
        
        # Prüfe ob OCR-Text ähnlich ist
        ocr_sim = self._ocr_text_similarity(step1, step2)
        if ocr_sim and ocr_sim > 0.7:
            reasons.append("Ähnlicher OCR-Text")
        
        # Prüfe Screenshot-Ähnlichkeit
        screenshot_sim = self._screenshot_similarity(step1, step2)
        if screenshot_sim and screenshot_sim > 0.8:
            reasons.append("Ähnliche Screenshots")
        
        if reasons:
            return ", ".join(reasons)
        
        return "Allgemeine Ähnlichkeit"
    
    def consolidate_steps(self, steps: List[Dict], suggestions: List[Dict]) -> List[Dict]:
        """
        Konsolidiert Schritte basierend auf Vorschlägen
        
        Args:
            steps: Liste von Schritten
            suggestions: Liste von Konsolidierungs-Vorschlägen
            
        Returns:
            Konsolidierte Liste von Schritten
        """
        if not suggestions:
            return steps
        
        # Erstelle Mapping von Schritt-Indizes zu konsolidierten Schritten
        consolidated_indices = set()
        consolidation_map = {}  # index -> neuer konsolidierter Schritt
        
        for suggestion in suggestions:
            idx1 = suggestion['step1_index']
            idx2 = suggestion['step2_index']
            
            # Überspringe wenn bereits konsolidiert
            if idx1 in consolidated_indices or idx2 in consolidated_indices:
                continue
            
            # Erstelle konsolidierten Schritt
            consolidated_step = self._merge_steps(steps[idx1], steps[idx2])
            
            # Verwende niedrigeren Index als Ziel
            target_idx = min(idx1, idx2)
            consolidation_map[target_idx] = consolidated_step
            consolidated_indices.add(idx1)
            consolidated_indices.add(idx2)
        
        # Erstelle neue Liste
        result = []
        for i, step in enumerate(steps):
            if i in consolidated_indices:
                if i in consolidation_map:
                    result.append(consolidation_map[i])
            else:
                result.append(step)
        
        # Aktualisiere Schritt-Nummern
        for i, step in enumerate(result, start=1):
            step['step_number'] = i
        
        return result
    
    def _merge_steps(self, step1: Dict, step2: Dict) -> Dict:
        """Verschmilzt zwei Schritte zu einem"""
        # Verwende Schritt mit niedrigerer Nummer als Basis
        base_step = step1 if step1.get('step_number', 0) < step2.get('step_number', 0) else step2
        
        # Erstelle konsolidierten Schritt
        merged = base_step.copy()
        
        # Kombiniere Beschreibungen
        desc1 = step1.get('description', '')
        desc2 = step2.get('description', '')
        
        if desc1 and desc2:
            # Verwende AI um Beschreibungen zu kombinieren
            merged_description = self._merge_descriptions_with_ai(desc1, desc2)
            if merged_description:
                merged['description'] = merged_description
        elif desc1:
            merged['description'] = desc1
        elif desc2:
            merged['description'] = desc2
        
        # Verwende Screenshot vom ersten Schritt
        merged['screenshot_path'] = step1.get('screenshot_path')
        
        # Aktualisiere Metadaten
        merged['consolidated'] = True
        merged['original_steps'] = [step1.get('step_number'), step2.get('step_number')]
        
        return merged
    
    def _merge_descriptions_with_ai(self, desc1: str, desc2: str) -> Optional[str]:
        """Verschmilzt zwei Beschreibungen mit AI"""
        try:
            prompt = f"""Kombiniere die folgenden zwei Beschreibungen zu einer präzisen, konsolidierten Beschreibung:

Beschreibung 1: {desc1}

Beschreibung 2: {desc2}

Kombiniere diese zu einer einzigen, klaren Beschreibung ohne Redundanzen."""
            
            merged = self.openai_client.generate_text(
                system_prompt="Du bist ein Experte für technische Dokumentation. Kombiniere Beschreibungen präzise.",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=300
            )
            
            return merged.strip() if merged else None
        
        except Exception as e:
            logger.warning(f"Fehler beim Verschmelzen von Beschreibungen: {e}")
            # Fallback: Verwende erste Beschreibung
            return desc1

