# Technical Writer Guide - Documentation-Tool-Generic

**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Target Audience:** Technical Writers, Documentation Creators, Content Authors

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Creating Documentation](#creating-documentation)
4. [Best Practices](#best-practices)
5. [Prompt Profiles](#prompt-profiles)
6. [Document Templates](#document-templates)
7. [Workflow Examples](#workflow-examples)
8. [Quality Guidelines](#quality-guidelines)
9. [Troubleshooting](#troubleshooting)
10. [Appendices](#appendices)

---

## Introduction

### Purpose

This guide helps technical writers create high-quality documentation using the Documentation-Tool-Generic application. It covers workflows, best practices, and techniques for producing professional documentation.

### What This Tool Does

Documentation-Tool-Generic automatically creates illustrated technical documentation by:
- Monitoring your actions as you use software
- Capturing screenshots at each step
- Extracting text using OCR
- Generating descriptions using AI
- Exporting in multiple formats (DOCX, PDF, Markdown, HTML)

### Use Cases

**Ideal For:**
- Standard Operating Procedures (SOPs)
- Training manuals
- User guides
- Technical documentation
- Process documentation
- Compliance documentation

**Not Ideal For:**
- Conceptual documentation (no screenshots)
- API documentation (code-focused)
- Architecture diagrams (static content)

---

## Getting Started

### Prerequisites

**Required:**
- Windows 10/11 computer
- Application installed and configured
- OpenAI API key configured
- Tesseract OCR installed

**Recommended:**
- Clean desktop environment
- Test data prepared
- Application to document ready

### First Steps

1. **Launch Application:**
   ```bash
   python main.py
   ```

2. **Configure Settings:**
   - Press F1 or click Settings
   - Enter OpenAI API key (if not in .env)
   - Select prompt profile (SOP, Training, or Technical)
   - Choose export formats

3. **Prepare Your Environment:**
   - Close unnecessary applications
   - Open the application to document
   - Clear desktop clutter
   - Prepare test data

4. **Start Your First Session:**
   - Click "Start Session" or press Ctrl+S
   - Perform the workflow you want to document
   - Click "End Session" or press Ctrl+Shift+S
   - Review generated documentation

---

## Creating Documentation

### Planning Your Documentation

**Before Starting:**

1. **Define Purpose:**
   - What is the documentation for?
   - Who is the target audience?
   - What should readers accomplish?

2. **Outline Steps:**
   - List major steps
   - Identify decision points
   - Note important details

3. **Prepare Test Data:**
   - Use realistic but non-sensitive data
   - Prepare sample files
   - Set up test accounts

4. **Choose Prompt Profile:**
   - **SOP**: Formal, compliant procedures
   - **Training**: Explanatory, educational
   - **Technical**: Precise, concise

### Recording Workflow

**Step-by-Step Process:**

1. **Start Session:**
   - Click "Start Session"
   - Verify status shows "Recording"

2. **Perform Actions:**
   - Work through your workflow
   - Move deliberately (not too fast)
   - Wait for UI updates
   - Let system capture each step

3. **Monitor Progress:**
   - Watch preview panel
   - Check step count
   - Verify screenshots are clear
   - Use Undo if needed (Ctrl+Z)

4. **Manage Session:**
   - Pause (Ctrl+P) for breaks
   - Undo mistakes immediately
   - Review steps periodically

5. **End Session:**
   - Click "End Session"
   - Wait for AI generation
   - Review generated documents

### Post-Processing

**After Generation:**

1. **Review Documents:**
   - Open DOCX or PDF file
   - Check AI-generated descriptions
   - Verify screenshot quality
   - Review step sequence

2. **Edit as Needed:**
   - Refine descriptions
   - Add context
   - Fix terminology
   - Improve clarity

3. **Finalize:**
   - Proofread content
   - Verify all steps
   - Check formatting
   - Export final versions

---

## Best Practices

### Preparation

**Desktop Environment:**
- Close unnecessary applications
- Clear desktop clutter
- Use clean backgrounds
- Ensure good screen resolution

**Application State:**
- Start from known state
- Use test data
- Clear caches if needed
- Reset to default settings

**Workflow Planning:**
- Practice workflow first
- Identify key steps
- Note decision points
- Plan for variations

### During Recording

**Pacing:**
- Move deliberately (not rushed)
- Wait for UI updates
- Pause between major steps
- Confirm each action

**Action Quality:**
- Use clear, obvious actions
- Avoid rapid clicking
- Wait for responses
- Verify each step captured

**Session Management:**
- Use Pause for breaks
- Undo mistakes immediately
- Review preview regularly
- Don't rush to finish

### Content Quality

**Step Descriptions:**
- One action per step
- Clear, actionable language
- Include expected outcomes
- Reference UI elements

**Screenshots:**
- Clear and readable
- Properly cropped
- Good contrast
- Relevant content visible

**Structure:**
- Logical flow
- Consistent terminology
- Appropriate detail level
- Complete coverage

---

## Prompt Profiles

### Understanding Prompt Profiles

Prompt profiles control the style and tone of AI-generated descriptions. Each profile is optimized for different documentation types.

### SOP Profile

**Use Case:** Standard Operating Procedures, compliance documentation

**Characteristics:**
- Formal, compliant language
- Imperative sentences ("Click the button")
- Technical terminology
- Step-by-step format
- Expected outcomes included

**Example Output:**
> Step 1: Login Dialog
> 
> Click in the 'Username' field and enter your username. Click in the 'Password' field and enter your password. Click the 'Login' button to proceed. The system will authenticate your credentials and display the main application window.

**When to Use:**
- Regulatory compliance documentation
- Standard operating procedures
- Formal process documentation
- Audit-ready documentation

### Training Profile

**Use Case:** Training manuals, user guides, educational content

**Characteristics:**
- Explanatory, educational tone
- Descriptive sentences with context
- Beginner-friendly language
- Learning objectives included
- Additional context provided

**Example Output:**
> Step 1: Login Dialog
> 
> You will see the login dialog, which is the first screen you encounter when starting the application. This dialog contains two text fields: one for your username and one for your password. The username field is located at the top, and the password field is below it. Both fields are empty when you first see them. At the bottom of the dialog, you'll find the 'Login' button. To log in, simply click in the username field, type your username, then click in the password field and type your password. Finally, click the 'Login' button to access the application.

**When to Use:**
- Training materials
- User onboarding guides
- Educational content
- Beginner-friendly documentation

### Technical Profile

**Use Case:** Technical documentation, developer guides, API documentation

**Characteristics:**
- Precise, concise language
- Short, direct statements
- Technical terminology (no explanation)
- Brief descriptions
- Focus on actions

**Example Output:**
> Step 1: Login Dialog
> 
> Access login dialog. Enter credentials in username and password fields. Click Login button to authenticate. System validates credentials and redirects to main interface.

**When to Use:**
- Technical documentation
- Developer guides
- API documentation
- Reference materials

### Creating Custom Profiles

**Step 1: Create Profile File**

Create `config/prompt_profiles/custom.yml`:

```yaml
name: custom
language: en
style: custom
description: "Custom documentation style"

system_prompt: |
  You are an expert documentation assistant...
  
step_template: |
  Generate a description for step {step_number}:
  
  Window Title: {window_title}
  OCR Text: {ocr_text}
  
  Previous Steps:
  {context}
  
  Create a description following the custom style.

introduction_template: |
  Create an introduction for {total_steps} steps...

conclusion_template: |
  Create a conclusion for the documentation...
```

**Step 2: Test Profile**

1. Select custom profile in settings
2. Create test session
3. Review generated output
4. Refine templates as needed

---

## Document Templates

### Understanding Templates

Document templates control the structure and formatting of generated documents. Templates define which sections to include and how to format them.

### Standard Template

**Sections Included:**
- Title page
- Table of contents
- Introduction
- Numbered steps with screenshots
- Conclusion
- Troubleshooting (optional)
- Security notes (optional)

**Configuration:**

Edit `config/document_templates/standard.yml`:

```yaml
name: standard
include_title_page: true
include_table_of_contents: true
include_introduction: true
include_conclusion: true
include_troubleshooting: false
include_security_notes: false
```

### Creating Custom Templates

**Step 1: Create Template File**

Create `config/document_templates/custom.yml`:

```yaml
name: custom
include_title_page: true
include_table_of_contents: true
include_introduction: true
include_conclusion: true
include_troubleshooting: true
include_security_notes: true
```

**Step 2: Use Template**

Select template when generating documents or configure as default.

---

## Workflow Examples

### Example 1: Simple Login Procedure

**Scenario:** Document a login process

**Steps:**
1. Start session
2. Open application
3. Click username field
4. Enter username
5. Click password field
6. Enter password
7. Click login button
8. End session

**Result:** 5-7 step documentation with screenshots

### Example 2: Complex Multi-Step Workflow

**Scenario:** Document complete data entry process

**Preparation:**
- Prepare test data
- Configure privacy masks
- Select Training profile

**Workflow:**
1. Login (3 steps)
2. Navigate to form (2 steps)
3. Fill form fields (10 steps)
4. Validate data (2 steps)
5. Submit form (1 step)
6. Review confirmation (1 step)

**Management:**
- Use Pause for data review
- Use Undo for corrections
- Monitor preview regularly

**Result:** Comprehensive 19-step training manual

### Example 3: Batch Documentation

**Scenario:** Document multiple related procedures

**Process:**
1. Document Session 1: Login
2. Document Session 2: Profile setup
3. Document Session 3: Password reset
4. Use batch processing
5. Combine into single manual

**Time Savings:** Process multiple sessions efficiently

---

## Quality Guidelines

### Content Quality

**Clarity:**
- Clear, actionable language
- One idea per sentence
- Logical flow
- Appropriate detail level

**Completeness:**
- All steps included
- Expected outcomes documented
- Error handling covered
- Prerequisites stated

**Accuracy:**
- Screenshots match descriptions
- Steps are correct
- Terminology consistent
- Information up-to-date

### Visual Quality

**Screenshots:**
- Clear and readable
- Properly cropped
- Good contrast
- Relevant content visible

**Formatting:**
- Consistent styling
- Proper headings
- Clear structure
- Professional appearance

### Review Checklist

**Before Finalizing:**
- [ ] All steps are accurate
- [ ] Screenshots are clear
- [ ] Descriptions are clear
- [ ] Terminology is consistent
- [ ] Formatting is correct
- [ ] No sensitive data exposed
- [ ] Links work (if applicable)
- [ ] Examples are realistic

---

## Troubleshooting

### Common Issues

#### Issue: Poor AI Descriptions

**Symptoms:**
- Descriptions are inaccurate
- Descriptions are unclear
- Wrong terminology used

**Solutions:**
- Try different prompt profile
- Use more capable model (gpt-5)
- Improve screenshot quality
- Check OCR text extraction
- Review and customize prompts

#### Issue: Missing Screenshots

**Symptoms:**
- Steps without screenshots
- Screenshots not captured

**Solutions:**
- Ensure window is visible
- Check trigger configuration
- Increase poll interval
- Verify application permissions

#### Issue: Too Many/Few Steps

**Symptoms:**
- Too many captures
- Missing important steps

**Solutions:**
- Adjust trigger configuration
- Change poll interval
- Modify change threshold
- Use manual capture (if available)

### Quality Improvement

**Better Descriptions:**
- Use appropriate prompt profile
- Ensure good screenshot quality
- Provide context in window titles
- Review and refine prompts

**Better Screenshots:**
- Use high resolution
- Ensure good contrast
- Clear desktop environment
- Proper window sizing

---

## Appendices

### Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Start Session |
| Ctrl+Shift+S | End Session |
| Ctrl+P | Pause/Resume |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| F1 | Open Settings |
| ESC | End Session (when active) |

### Appendix B: File Locations

**Configuration:**
- Prompt profiles: `config/prompt_profiles/`
- Document templates: `config/document_templates/`
- Trigger config: `config/trigger_config.yml`
- Privacy mask: `config/privacy_mask.yml`

**Output:**
- Generated documents: `data/output/`
- Session data: `data/sessions/`
- Screenshots: `data/screenshots/`

### Appendix C: Resources

**Documentation:**
- [User Manual](../USER_MANUAL.md)
- [Documentation Standards](DOCUMENTATION_STANDARDS.md)
- [Administrator Manual](ADMINISTRATOR_MANUAL.md)

**External:**
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Tesseract OCR Documentation](https://tesseract-ocr.github.io/)

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Maintained By:** Technical Writing Team

