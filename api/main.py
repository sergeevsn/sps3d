from typing import Annotated
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from io import BytesIO
from pathlib import Path
import pandas as pd

import os
import shutil

from utils.spsio import REV21_REC_FORMAT, REV21_REL_FORMAT, REV21_SOU_FORMAT
from utils.spsio import SPSReceiverReader, SPSSourceReader, SPSRelationReader
from utils.spsio import get_pattern_by_source_coords

app = FastAPI()

UPLOAD_FOLDER = 'SPS'
TEST_R_FNAME =  'test.rps'
TEST_S_FNAME =  'test.sps'
TEST_X_FNAME =  'test.xps'
TEST_R_FMT_FNAME =  'test_r.fmt'
TEST_S_FMT_FNAME =  'test_s.fmt'
TEST_X_FMT_FNAME =  'test_x.fmt'

@app.on_event("shutdown")
def ob_shutdown():      
    for fname in os.listdir(UPLOAD_FOLDER):
        if (os.path.exists(os.path.join(UPLOAD_FOLDER, fname))) and (not fname in [TEST_R_FNAME, TEST_S_FNAME, TEST_X_FNAME, TEST_R_FMT_FNAME, TEST_S_FMT_FNAME, TEST_X_FMT_FNAME]):
            os.remove(os.path.join(UPLOAD_FOLDER, fname))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)            

def get_data(host):
    receivers = pd.DataFrame()
    rFileName = os.path.join(UPLOAD_FOLDER, f'{host}_R.sps')
    rFormatFileName = os.path.join(UPLOAD_FOLDER, f'{host}_R.fmt')
    if os.path.exists(rFileName) and os.path.exists(rFormatFileName):
        with open(rFormatFileName) as f:
            rFormat = f.read()         
            print('R Format: ', rFormat)   
        rr = SPSReceiverReader(rFormat)        
        receivers = rr.read(os.path.join(UPLOAD_FOLDER, f'{host}_R.sps'))
        print('Receivers: ', receivers)
    sources = pd.DataFrame()
    sFileName = os.path.join(UPLOAD_FOLDER, f'{host}_S.sps')
    sFormatFileName = os.path.join(UPLOAD_FOLDER, f'{host}_S.fmt')
    if os.path.exists(sFileName) and os.path.exists(sFormatFileName):      
        with open(sFormatFileName) as f:
            sFormat = f.read()
        sr = SPSSourceReader(sFormat)
        sources = sr.read(os.path.join(UPLOAD_FOLDER, f'{host}_S.sps'))        
    relations = pd.DataFrame()
    xFileName = os.path.join(UPLOAD_FOLDER, f'{host}_X.sps')
    xFormatFileName = os.path.join(UPLOAD_FOLDER, f'{host}_X.fmt')
    if os.path.exists(xFileName) and os.path.exists(xFormatFileName):
        with open(xFormatFileName) as f:
            xFormat = f.read()
        xr = SPSRelationReader(xFormat)
        relations = xr.read(os.path.join(UPLOAD_FOLDER, f'{host}_X.sps'))
    return receivers, sources, relations    

def get_sending(host):
    receivers, sources, relations = get_data(host)   
    sending = {}
    if len(receivers)>0:
        sending['rec_x'] = receivers['X'].values.tolist()
        sending['rec_y'] = receivers['Y'].values.tolist()   
    if len(sources)>0:
        sending['sou_x'] = sources['X'].values.tolist()
        sending['sou_y'] = sources['Y'].values.tolist()   
    if len(sources)>0 and len(receivers)>0 and len(relations)>0:
        soux = sources.X[len(sources)//2]
        souy = sources.Y[len(sources)//2]    
        pattern =  get_pattern_by_source_coords(soux, souy, sources, receivers, relations)       
        sending['pat_x'] = pattern['X'].values.tolist()
        sending['pat_y'] = pattern['Y'].values.tolist()
        sending['sel_sou_x'] = [soux.tolist()]
        sending['sel_sou_y'] = [souy.tolist()]     
    return sending

@app.post('/update')
async def update_pattern(request: Request):   
    coords = await request.json()
    receivers, sources, relations = get_data(request.client.host)
    pattern = get_pattern_by_source_coords(coords[0], coords[1], sources, receivers, relations)
    return {'x': pattern.X.to_list(), 'y': pattern.Y.to_list()}

    
@app.get('/testdata')
async def get_testdata(request: Request):    
    shutil.copyfile(os.path.join(UPLOAD_FOLDER, TEST_R_FNAME), os.path.join(UPLOAD_FOLDER, f'{request.client.host}_R.sps'))    
    shutil.copyfile(os.path.join(UPLOAD_FOLDER, TEST_S_FNAME), os.path.join(UPLOAD_FOLDER, f'{request.client.host}_S.sps'))  
    shutil.copyfile(os.path.join(UPLOAD_FOLDER, TEST_X_FNAME), os.path.join(UPLOAD_FOLDER, f'{request.client.host}_X.sps')) 
    shutil.copyfile(os.path.join(UPLOAD_FOLDER, TEST_R_FMT_FNAME), os.path.join(UPLOAD_FOLDER, f'{request.client.host}_R.fmt'))    
    shutil.copyfile(os.path.join(UPLOAD_FOLDER, TEST_S_FMT_FNAME), os.path.join(UPLOAD_FOLDER, f'{request.client.host}_S.fmt'))  
    shutil.copyfile(os.path.join(UPLOAD_FOLDER, TEST_X_FMT_FNAME), os.path.join(UPLOAD_FOLDER, f'{request.client.host}_X.fmt'))  
    
    sending = get_sending(request.client.host) 
    return sending

@app.post('/upload')
async def update(request: Request, 
                  rFile: UploadFile = File(None),
                  rFormat: str = Form(None),
                  sFile: UploadFile = File(None),
                  sFormat: str = Form(None),
                  xFile: UploadFile = File(None),
                  xFormat: str = Form(None)):
      # Save the files      
    if rFile:  
        with open(os.path.join(UPLOAD_FOLDER, f'{request.client.host}_R.sps'), "wb") as buffer:
            shutil.copyfileobj(rFile.file, buffer)
        with open(os.path.join(UPLOAD_FOLDER, f'{request.client.host}_R.fmt'), "w") as fmt:            
            if rFormat == "rev2.1":
                rFormat = REV21_REC_FORMAT
            fmt.write(rFormat)
    if sFile:
        with open(os.path.join(UPLOAD_FOLDER,  f'{request.client.host}_S.sps'), "wb") as buffer:
            shutil.copyfileobj(sFile.file, buffer)
        with open(os.path.join(UPLOAD_FOLDER, f'{request.client.host}_S.fmt'), "w") as fmt:
            if sFormat == "rev2.1":
                sFormat = REV21_SOU_FORMAT
            fmt.write(sFormat)    
    if xFile:
        with open(os.path.join(UPLOAD_FOLDER,  f'{request.client.host}_X.sps'), "wb") as buffer:
            shutil.copyfileobj(xFile.file, buffer)
        with open(os.path.join(UPLOAD_FOLDER, f'{request.client.host}_X.fmt'), "w") as fmt:
            if xFormat == "rev2.1":
                xFormat = REV21_REL_FORMAT
            fmt.write(xFormat)    
    sending = get_sending(request.client.host)
    return sending