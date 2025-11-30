"""
SCORM Exporter - Exports tutorials in SCORM format.
Part of Feature 5: Interactive Tutorial Generator
"""

import zipfile
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SCORMExporter:
    """
    Exports tutorials in SCORM 2004 format for LMS integration.
    """
    
    SCORM_VERSION = "2004 4th Edition"
    
    def __init__(self, organization_id: str = "AHG"):
        """
        Initialize SCORM exporter.
        
        Args:
            organization_id: Organization identifier
        """
        self.organization_id = organization_id
        logger.info("SCORMExporter initialized")
    
    def export(
        self,
        tutorial: Any,
        output_path: str,
        html_content: str
    ) -> str:
        """
        Export tutorial as SCORM package.
        
        Args:
            tutorial: Tutorial object
            output_path: Output ZIP file path
            html_content: HTML content of tutorial
            
        Returns:
            Path to created package
        """
        package_dir = Path(output_path).parent / f"scorm_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        package_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Create manifest
            manifest = self._create_manifest(tutorial)
            (package_dir / "imsmanifest.xml").write_text(manifest, encoding='utf-8')
            
            # Create content directory
            content_dir = package_dir / "content"
            content_dir.mkdir(exist_ok=True)
            
            # Save HTML content with SCORM API integration
            scorm_html = self._add_scorm_api(html_content, tutorial)
            (content_dir / "index.html").write_text(scorm_html, encoding='utf-8')
            
            # Create SCORM API wrapper
            api_js = self._create_scorm_api()
            (content_dir / "scorm-api.js").write_text(api_js, encoding='utf-8')
            
            # Create ZIP package
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in package_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(package_dir)
                        zf.write(file_path, arcname)
            
            logger.info(f"Exported SCORM package to: {output_path}")
            return output_path
        
        finally:
            # Cleanup temp directory
            import shutil
            shutil.rmtree(package_dir, ignore_errors=True)
    
    def _create_manifest(self, tutorial: Any) -> str:
        """Create SCORM manifest XML."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{self.organization_id}_{tutorial.id}"
    xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3"
    xmlns:adlseq="http://www.adlnet.org/xsd/adlseq_v1p3"
    xmlns:adlnav="http://www.adlnet.org/xsd/adlnav_v1p3"
    xmlns:imsss="http://www.imsglobal.org/xsd/imsss">
    
    <metadata>
        <schema>ADL SCORM</schema>
        <schemaversion>{self.SCORM_VERSION}</schemaversion>
    </metadata>
    
    <organizations default="ORG-{tutorial.id}">
        <organization identifier="ORG-{tutorial.id}">
            <title>{tutorial.title}</title>
            <item identifier="ITEM-{tutorial.id}" identifierref="RES-{tutorial.id}">
                <title>{tutorial.title}</title>
                <imsss:sequencing>
                    <imsss:deliveryControls completionSetByContent="true" objectiveSetByContent="true"/>
                </imsss:sequencing>
            </item>
        </organization>
    </organizations>
    
    <resources>
        <resource identifier="RES-{tutorial.id}" type="webcontent" adlcp:scormType="sco" href="content/index.html">
            <file href="content/index.html"/>
            <file href="content/scorm-api.js"/>
        </resource>
    </resources>
</manifest>'''
    
    def _add_scorm_api(self, html_content: str, tutorial: Any) -> str:
        """Add SCORM API calls to HTML content."""
        # Add SCORM initialization and tracking
        scorm_script = f'''
<script src="scorm-api.js"></script>
<script>
    // Initialize SCORM
    window.addEventListener('load', function() {{
        if (typeof ScormAPI !== 'undefined') {{
            ScormAPI.initialize();
            ScormAPI.setLessonStatus('incomplete');
        }}
    }});
    
    // Override complete function
    var originalComplete = typeof complete === 'function' ? complete : function() {{}};
    function complete() {{
        if (typeof ScormAPI !== 'undefined') {{
            ScormAPI.setLessonStatus('completed');
            ScormAPI.setScore(100, 100, 0);
            ScormAPI.commit();
            ScormAPI.terminate();
        }}
        originalComplete();
    }}
    
    // Track progress
    var totalSteps = {len(tutorial.steps)};
    var originalShowStep = typeof showStep === 'function' ? showStep : function() {{}};
    function showStep(n) {{
        originalShowStep(n);
        if (typeof ScormAPI !== 'undefined') {{
            var progress = (n / totalSteps) * 100;
            ScormAPI.setProgress(progress);
        }}
    }}
</script>
'''
        
        # Insert before closing body tag
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', scorm_script + '</body>')
        else:
            html_content += scorm_script
        
        return html_content
    
    def _create_scorm_api(self) -> str:
        """Create SCORM API JavaScript wrapper."""
        return '''/**
 * SCORM 2004 API Wrapper
 */
var ScormAPI = (function() {
    var api = null;
    var initialized = false;
    
    function findAPI(win) {
        var attempts = 0;
        while ((win.API_1484_11 == null) && (win.parent != null) && (win.parent != win)) {
            attempts++;
            if (attempts > 10) return null;
            win = win.parent;
        }
        return win.API_1484_11;
    }
    
    function getAPI() {
        if (api == null) {
            api = findAPI(window);
            if (api == null && window.opener != null) {
                api = findAPI(window.opener);
            }
        }
        return api;
    }
    
    return {
        initialize: function() {
            var api = getAPI();
            if (api != null) {
                var result = api.Initialize("");
                initialized = (result === "true" || result === true);
            }
            return initialized;
        },
        
        terminate: function() {
            var api = getAPI();
            if (api != null && initialized) {
                api.Terminate("");
                initialized = false;
            }
        },
        
        setLessonStatus: function(status) {
            var api = getAPI();
            if (api != null && initialized) {
                api.SetValue("cmi.completion_status", status);
                api.SetValue("cmi.success_status", status === "completed" ? "passed" : "unknown");
            }
        },
        
        setScore: function(score, max, min) {
            var api = getAPI();
            if (api != null && initialized) {
                api.SetValue("cmi.score.raw", score);
                api.SetValue("cmi.score.max", max);
                api.SetValue("cmi.score.min", min);
                api.SetValue("cmi.score.scaled", score / max);
            }
        },
        
        setProgress: function(percent) {
            var api = getAPI();
            if (api != null && initialized) {
                api.SetValue("cmi.progress_measure", percent / 100);
            }
        },
        
        commit: function() {
            var api = getAPI();
            if (api != null && initialized) {
                api.Commit("");
            }
        }
    };
})();
'''

