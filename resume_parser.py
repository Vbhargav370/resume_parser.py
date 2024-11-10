import os
import pdfplumber
import re
import tkinter as tk
from tkinter import filedialog, messagebox

SECTORS = {
    "IT": ["python", "java", "c", "c++", "html", "css", "software development", "data analysis", "cloud computing", "ai", "machine learning"],
    "Design": ["ui/ux", "figma", "adobe", "sketch", "design"],
    "Finance": ["accounting", "finance", "financial analysis", "investment", "banking", "financial modeling"],
    "Sales": ["sales", "marketing", "client relationship", "business development", "crm"]
}

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                text += page_text if page_text else ""
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_information(text):
    text_lines = text.splitlines()  
    text_lower = text.lower()
    
    phone_numbers = re.findall(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)


    name = "Not Found"
    for line in text_lines[:5]:  
        if len(line.strip()) > 2 and not any(keyword in line.lower() for keyword in ["email", "phone", "linkedin", "github", "address"]):
            name = line.strip().title()
            break
    
    if name == "Not Found":

        declaration_match = re.search(r"declaration.*?([a-z\s]{3,25})\s*\n", text, re.DOTALL)
        if declaration_match:
            name = declaration_match.group(1).strip().title()
    

    skill_keywords = ["python", "java", "c", "c++", "html", "css"]
    skills_found = [skill.capitalize() for skill in skill_keywords if skill in text_lower]
    
    project_pattern = r"projects.*?[\n|•](.*?)\n"
    projects = re.findall(project_pattern, text, re.DOTALL)
    projects = [proj.strip("• ").capitalize() for proj in projects if proj]
    
    projects = [proj for proj in projects if "education" not in proj.lower()]
    

    matched_sectors = []
    for sector, keywords in SECTORS.items():
        if any(skill.lower() in keywords for skill in skills_found):
            matched_sectors.append(sector)

    return {
        "name": name,
        "email": emails[0] if emails else "N/A",
        "phone": phone_numbers[0] if phone_numbers else "N/A",
        "skills_found": skills_found,
        "projects": projects,
        "sectors": matched_sectors if matched_sectors else ["No sector match found"]
    }

def parse_resume(file_path):
    text = extract_text_from_pdf(file_path)
    return extract_information(text) if text else {}

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        parsed_resume = parse_resume(file_path)
        if parsed_resume:
            display_resume(parsed_resume)
        else:
            messagebox.showerror("Error", "Failed to parse the resume.")

def display_resume(parsed_resume):
    output_text.delete(1.0, tk.END)
    
    output_text.insert(tk.END, f"Name: {parsed_resume.get('name', 'N/A')}\n")
    output_text.insert(tk.END, f"Email: {parsed_resume.get('email', 'N/A')}\n")
    output_text.insert(tk.END, f"Phone: {parsed_resume.get('phone', 'N/A')}\n")
    output_text.insert(tk.END, f"Skills Found: {', '.join(parsed_resume.get('skills_found', ['N/A']))}\n")
    
    output_text.insert(tk.END, "Projects:\n")
    for project in parsed_resume.get('projects', ['N/A']):
        output_text.insert(tk.END, f"  - {project}\n")
    
    output_text.insert(tk.END, f"Eligible Sectors: {', '.join(parsed_resume.get('sectors', ['No sector match found']))}\n")

root = tk.Tk()
root.title("Resume Parser")
root.geometry("600x500")

browse_button = tk.Button(root, text="Browse Resume", command=browse_file, width=20)
browse_button.pack(pady=20)

output_text = tk.Text(root, height=20, width=70)
output_text.pack(padx=20, pady=10)

root.mainloop()
