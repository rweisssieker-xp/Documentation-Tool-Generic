"""
BPMN Exporter - Exports process models to BPMN 2.0 format.
Part of Feature 2: Process Mining Engine
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BPMNExporter:
    """
    Exports process models to BPMN 2.0 XML format.
    """
    
    BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
    BPMNDI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"
    DC_NS = "http://www.omg.org/spec/DD/20100524/DC"
    DI_NS = "http://www.omg.org/spec/DD/20100524/DI"
    
    def __init__(self):
        """Initialize BPMN exporter."""
        logger.info("BPMNExporter initialized")
    
    def export(
        self,
        process_model: Any,
        output_path: str,
        include_layout: bool = True
    ) -> str:
        """
        Export process model to BPMN file.
        
        Args:
            process_model: ProcessModel object
            output_path: Output file path
            include_layout: Include diagram layout
            
        Returns:
            Generated BPMN XML
        """
        # Create root element with namespaces
        root = ET.Element("definitions")
        root.set("xmlns", self.BPMN_NS)
        root.set("xmlns:bpmndi", self.BPMNDI_NS)
        root.set("xmlns:dc", self.DC_NS)
        root.set("xmlns:di", self.DI_NS)
        root.set("id", f"Definitions_{process_model.id}")
        root.set("targetNamespace", "http://ahg.documentation/bpmn")
        
        # Create process element
        process = ET.SubElement(root, "process")
        process.set("id", f"Process_{process_model.id}")
        process.set("name", process_model.name)
        process.set("isExecutable", "false")
        
        # Add start event
        start = ET.SubElement(process, "startEvent")
        start.set("id", "StartEvent_1")
        start.set("name", "Start")
        
        # Add activities (tasks)
        activity_ids = {}
        for i, activity in enumerate(process_model.activities):
            task = ET.SubElement(process, "task")
            task_id = f"Activity_{i+1}"
            task.set("id", task_id)
            task.set("name", activity)
            activity_ids[activity] = task_id
        
        # Add end event
        end = ET.SubElement(process, "endEvent")
        end.set("id", "EndEvent_1")
        end.set("name", "End")
        
        # Add sequence flows
        flow_count = 0
        
        # Flows from start to first activities
        for start_act in process_model.start_activities:
            if start_act in activity_ids:
                flow_count += 1
                flow = ET.SubElement(process, "sequenceFlow")
                flow.set("id", f"Flow_{flow_count}")
                flow.set("sourceRef", "StartEvent_1")
                flow.set("targetRef", activity_ids[start_act])
        
        # Flows between activities
        for from_act, to_acts in process_model.transitions.items():
            if from_act not in activity_ids:
                continue
            for to_act in to_acts:
                if to_act not in activity_ids:
                    continue
                flow_count += 1
                flow = ET.SubElement(process, "sequenceFlow")
                flow.set("id", f"Flow_{flow_count}")
                flow.set("sourceRef", activity_ids[from_act])
                flow.set("targetRef", activity_ids[to_act])
        
        # Flows from last activities to end
        for end_act in process_model.end_activities:
            if end_act in activity_ids:
                flow_count += 1
                flow = ET.SubElement(process, "sequenceFlow")
                flow.set("id", f"Flow_{flow_count}")
                flow.set("sourceRef", activity_ids[end_act])
                flow.set("targetRef", "EndEvent_1")
        
        # Add diagram if requested
        if include_layout:
            self._add_diagram(root, process_model, activity_ids)
        
        # Format and save
        xml_str = self._prettify(root)
        Path(output_path).write_text(xml_str, encoding='utf-8')
        
        logger.info(f"Exported BPMN to: {output_path}")
        return xml_str
    
    def export_to_mermaid(self, process_model: Any) -> str:
        """
        Export process model to Mermaid diagram format.
        
        Args:
            process_model: ProcessModel object
            
        Returns:
            Mermaid diagram string
        """
        lines = ["graph LR"]
        
        # Add start
        lines.append("    Start((Start))")
        
        # Add activities
        for activity in process_model.activities:
            safe_name = activity.replace(" ", "_").replace("-", "_")
            lines.append(f"    {safe_name}[{activity}]")
        
        # Add end
        lines.append("    End((End))")
        
        # Add flows from start
        for start_act in process_model.start_activities:
            safe_name = start_act.replace(" ", "_").replace("-", "_")
            lines.append(f"    Start --> {safe_name}")
        
        # Add transitions
        for from_act, to_acts in process_model.transitions.items():
            from_safe = from_act.replace(" ", "_").replace("-", "_")
            for to_act in to_acts:
                to_safe = to_act.replace(" ", "_").replace("-", "_")
                lines.append(f"    {from_safe} --> {to_safe}")
        
        # Add flows to end
        for end_act in process_model.end_activities:
            safe_name = end_act.replace(" ", "_").replace("-", "_")
            lines.append(f"    {safe_name} --> End")
        
        # Add styling
        lines.append("")
        lines.append("    style Start fill:#90EE90")
        lines.append("    style End fill:#FFB6C1")
        
        return "\n".join(lines)
    
    def _add_diagram(
        self,
        root: ET.Element,
        process_model: Any,
        activity_ids: Dict[str, str]
    ) -> None:
        """Add BPMN diagram layout."""
        diagram = ET.SubElement(root, "{%s}BPMNDiagram" % self.BPMNDI_NS)
        diagram.set("id", "BPMNDiagram_1")
        
        plane = ET.SubElement(diagram, "{%s}BPMNPlane" % self.BPMNDI_NS)
        plane.set("id", "BPMNPlane_1")
        plane.set("bpmnElement", f"Process_{process_model.id}")
        
        # Layout start event
        self._add_shape(plane, "StartEvent_1", 150, 200, 36, 36)
        
        # Layout activities
        x = 250
        for i, activity in enumerate(process_model.activities):
            task_id = activity_ids.get(activity)
            if task_id:
                self._add_shape(plane, task_id, x, 180, 100, 80)
                x += 150
        
        # Layout end event
        self._add_shape(plane, "EndEvent_1", x, 200, 36, 36)
    
    def _add_shape(
        self,
        plane: ET.Element,
        element_id: str,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> None:
        """Add a shape to the diagram."""
        shape = ET.SubElement(plane, "{%s}BPMNShape" % self.BPMNDI_NS)
        shape.set("id", f"{element_id}_di")
        shape.set("bpmnElement", element_id)
        
        bounds = ET.SubElement(shape, "{%s}Bounds" % self.DC_NS)
        bounds.set("x", str(x))
        bounds.set("y", str(y))
        bounds.set("width", str(width))
        bounds.set("height", str(height))
    
    def _prettify(self, elem: ET.Element) -> str:
        """Return a pretty-printed XML string."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

