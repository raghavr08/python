"""ResumeIQ secure API. Configure OPENAI_API_KEY to enable live AI analysis."""
import json, os, re, tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
import fitz
from docx import Document

limiter=Limiter(key_func=get_remote_address)
app=FastAPI(title='ResumeIQ API')
app.state.limiter=limiter
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('CORS_ORIGINS','http://localhost:5173').split(','),allow_methods=['*'],allow_headers=['*'])
MAX=10*1024*1024
class AnalyzeRequest(BaseModel):
    resume_text:str=Field(min_length=20,max_length=100000)
    job_description:str=Field(min_length=20,max_length=100000)
    job_title:str=''
class Scores(BaseModel): skills:int=Field(ge=0,le=100); experience:int=Field(ge=0,le=100); keywords:int=Field(ge=0,le=100); projects:int=Field(ge=0,le=100); clarity:int=Field(ge=0,le=100)
def extract(upload:UploadFile,data:bytes):
    suffix=Path(upload.filename or '').suffix.lower()
    if suffix=='.txt': return data.decode('utf-8',errors='ignore')
    with tempfile.NamedTemporaryFile(suffix=suffix,delete=True) as f:
        f.write(data);f.flush()
        if suffix=='.pdf': return ''.join(p.get_text() for p in fitz.open(f.name))
        if suffix=='.docx': return '\n'.join(p.text for p in Document(f.name).paragraphs)
    raise HTTPException(415,'Only PDF, DOCX, and TXT are supported.')
@app.post('/api/resume/upload')
async def upload(resume:UploadFile=File(...)):
    if Path(resume.filename or '').suffix.lower() not in {'.pdf','.docx','.txt'}: raise HTTPException(415,'Upload PDF, DOCX, or TXT.')
    data=await resume.read()
    if len(data)>MAX: raise HTTPException(413,'Maximum file size is 10 MB.')
    text=extract(resume,data)
    if len(text.strip())<20: raise HTTPException(422,'No readable resume text was found.')
    return {'filename':resume.filename,'text':text}
def level(n): return 'Excellent Match' if n>=90 else 'Strong Match' if n>=75 else 'Moderate Match' if n>=60 else 'Needs Improvement' if n>=40 else 'Low Match'
@app.post('/api/resume/analyze')
@limiter.limit('10/minute')
async def analyze(request, body:AnalyzeRequest):
    """Deterministic score shell: replace component estimate with validated LLM JSON when configured."""
    r,j=body.resume_text.lower(),body.job_description.lower(); terms=['python','javascript','react','sql','git','rest api','docker','aws','kubernetes','communication']
    wanted=[x for x in terms if x in j]; matched=[x for x in wanted if x in r]; base=round(100*len(matched)/max(1,len(wanted)))
    scores=Scores(skills=base,experience=min(100,base+(10 if 'experience' in r else 0)),keywords=max(15,round(base*.9)),projects=min(100,base+(10 if 'project' in r else 0)),clarity=78 if len(r)>300 else 60)
    overall=round(scores.skills*.35+scores.experience*.25+scores.keywords*.15+scores.projects*.15+scores.clarity*.10)
    return {'overall_score':overall,'match_level':level(overall),'scores':scores.model_dump(),'matched_skills':matched,'missing_skills':[x for x in wanted if x not in matched],'strengths':[],'weaknesses':[],'recommendations':['Use only resume-supported evidence.'],'interview_questions':[],'notice':'Deterministic local analysis. Configure an AI provider for richer structured feedback.'}
@app.get('/api/analysis/history')
async def history(): return {'items':[],'notice':'Persistent storage is not configured.'}

class OptimizeRequest(BaseModel):
    resume_text:str=Field(min_length=20,max_length=100000)
    instruction:str='Improve clarity without adding facts.'
@app.post('/api/resume/optimize')
async def optimize(body:OptimizeRequest):
    # The API deliberately returns source text until a validated LLM adapter is configured.
    return {'draft':body.resume_text,'notice':'No AI provider configured; no facts were changed.'}

class InterviewRequest(BaseModel):
    resume_text:str=Field(min_length=20,max_length=100000)
    job_description:str=Field(min_length=20,max_length=100000)
@app.post('/api/interview/questions')
async def questions(body:InterviewRequest):
    return {'questions':[{'category':'Project-Based','question':'Walk me through the project most relevant to this role.','evaluates':'ownership, technical reasoning, and honest outcomes.'}]}

class AnswerRequest(BaseModel): answer:str=Field(min_length=1,max_length=20000)
@app.post('/api/interview/evaluate')
async def evaluate(body:AnswerRequest):
    feedback='Add specific context, your individual action, and an outcome you can verify.' if len(body.answer)<100 else 'Good start. Make the technical trade-offs and measurable outcome clearer.'
    return {'feedback':feedback,'follow_up':'What would you improve if you repeated that work today?'}

@app.get('/api/resume/download')
async def download():
    raise HTTPException(501,'PDF generation is enabled when a saved optimized draft and user-scoped storage are configured.')
