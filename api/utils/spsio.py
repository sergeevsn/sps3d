import pandas as pd
import os

REV21_REC_FORMAT = "LINE:2:11,POINT:12:21,X:47:55,Y:56:65,Z:66:71"
REV21_SOU_FORMAT = "LINE:2:11,POINT:12:21,UPHOLE:39:40,DEPTH:41:46,X:47:55,Y:56:65,Z:66:71"
REV21_REL_FORMAT = "SLINE:18:27,SPOINT:28:37,FROMCH:39:43,TOCH:44:48,RLINE:50:59,FROMREC:60:69,TOREC:70:79"


def parse_pos_content(pos_content: list):   
    return [int(pos_content[0]), int(pos_content[1])]

def parse_number(input_string: str):
    cleaned_string = ''.join(char for char in input_string if (char.isdigit() or char=='.'))
    try:
        result = round(float(cleaned_string))
    except:
        result = None
    return result   


class SPSReader:
    source_fname : str = ""
    format : str = ""
    all_lines = False
    def __init__(self, format : str, all_lines : bool) -> None:
        self.format = format
        self.all_lines = all_lines
    def read(self, fname):        
        if not os.path.exists(fname):
            print(f"File {fname} doesn't exist!")
            return False        
        if self.format == "":
            print("Format is not set!")
            return False
        return True

class SPSReceiverReader(SPSReader):
    line_pos : list = []
    point_pos : list = []
    x_pos : list = []
    y_pos : list = []
    elev_pos : list = []    
    def __init__(self, format=REV21_REC_FORMAT, all_lines=False) -> None:
        super().__init__(format, all_lines)
        positions = format.split(',') 
        for pos in positions:
            pos_content = pos.split(':')
           
            if pos_content[0] == 'LINE':
                self.line_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'POINT':
                self.point_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'X':
                self.x_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'Y':
                self.y_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'Z':
                self.elev_pos = parse_pos_content(pos_content[1:])    
        
    def read(self, fname) -> pd.DataFrame:
        lines = []
        points = []
        x_coords = []
        y_coords = []
        elevations = []
        if super().read(fname):
            with open(fname) as recf:
                for file_line in recf:
                    if file_line[0] == 'R' or self.all_lines:    
                        if self.line_pos[1] > self.line_pos[0]: 
                            lines.append(parse_number(file_line[self.line_pos[0]-1:self.line_pos[1]]))
                        if self.point_pos[1] > self.point_pos[0]: 
                            points.append(parse_number(file_line[self.point_pos[0]-1:self.point_pos[1]]))
                        if self.x_pos[1] > self.x_pos[0]: 
                            x_coords.append(parse_number(file_line[self.x_pos[0]-1:self.x_pos[1]]))
                        if self.y_pos[1] > self.y_pos[0]: 
                            y_coords.append(parse_number(file_line[self.y_pos[0]-1:self.y_pos[1]]))
                        if self.elev_pos[1] > self.elev_pos[0]: 
                            elevations.append(parse_number(file_line[self.elev_pos[0]-1:self.elev_pos[1]]))
        else:
            return None
        return pd.DataFrame({'Line': lines, 'Point': points, 'X': x_coords, 'Y': y_coords, 'Elev': elevations})
    
class SPSSourceReader(SPSReader):
    line_pos : list = []
    point_pos : list = []
    uphole_pos : list = []
    depth_pos : list = []
    x_pos : list = []
    y_pos : list = []
    elev_pos : list = []
    def __init__(self, format=REV21_SOU_FORMAT, all_lines=False) -> None:
        super().__init__(format, all_lines)
        positions = format.split(',') 
        for pos in positions:
            pos_content = pos.split(':')
            if pos_content[0] == 'LINE':
                self.line_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'POINT':
                self.point_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'UPHOLE':
                self.uphole_pos = parse_pos_content(pos_content[1:])    
            if pos_content[0] == 'DEPTH':
                self.depth_pos = parse_pos_content(pos_content[1:])    
            if pos_content[0] == 'X':
                self.x_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'Y':
                self.y_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'Z':
                self.elev_pos = parse_pos_content(pos_content[1:])    
        
    def read(self, fname) -> pd.DataFrame:      
        lines = []
        points = []
        upholes = []
        depths = []
        x_coords = []
        y_coords = []
        elevations = []
        if super().read(fname):
            with open(fname) as souf:
                for file_line in souf:                   
                    if file_line[0] == 'S' or self.all_lines:                    
                      
                        if self.line_pos[1] > self.line_pos[0]:
                            lines.append(parse_number(file_line[self.line_pos[0]-1:self.line_pos[1]]))
                        if self.point_pos[1] > self.point_pos[0]:    
                            points.append(parse_number(file_line[self.point_pos[0]-1:self.point_pos[1]]))
                        if self.uphole_pos[1] > self.uphole_pos[0]:
                            upholes.append(parse_number(file_line[self.uphole_pos[0]-1: self.uphole_pos[1]]))
                        if self.depth_pos[1] > self.depth_pos[0]:
                            depths.append(parse_number(file_line[self.depth_pos[0]-1: self.depth_pos[1]]))
                        if self.x_pos[1] > self.x_pos[0]:    
                            x_coords.append(parse_number(file_line[self.x_pos[0]-1:self.x_pos[1]]))
                        if self.y_pos[1] > self.y_pos[0]:    
                            y_coords.append(parse_number(file_line[self.y_pos[0]-1:self.y_pos[1]]))
                        if self.elev_pos[1] > self.elev_pos[0]:    
                            elevations.append(parse_number(file_line[self.elev_pos[0]-1:self.elev_pos[1]]))
        else:
            return None
        return pd.DataFrame({'Line': lines, 'Point': points, 'Uphole': upholes, 'Depth': depths, 'X': x_coords, 'Y': y_coords, 'Elev': elevations})


class SPSRelationReader(SPSReader):
    sline_pos : list = []
    spoint_pos : list = []
    fromch_pos : list = []
    toch_pos : list = []
    rline_pos : list = []
    fromrec_pos : list = []
    torec_pos : list = []
   
    def __init__(self, format=REV21_REL_FORMAT, all_lines=False) -> None:
        super().__init__(format, all_lines)
        positions = format.split(',') 
        for pos in positions:            
            pos_content = pos.split(':')            
            if pos_content[0] == 'SLINE':
                self.sline_pos = parse_pos_content(pos_content[1:])               
            if pos_content[0] == 'SPOINT':
                self.spoint_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'FROMCH':
                self.fromch_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'TOCH':
                self.toch_pos = parse_pos_content(pos_content[1:])
            if pos_content[0] == 'RLINE':
                self.rline_pos = parse_pos_content(pos_content[1:])    
            if pos_content[0] == 'FROMREC':
                self.fromrec_pos = parse_pos_content(pos_content[1:])   
            if pos_content[0] == 'TOREC':
                self.torec_pos = parse_pos_content(pos_content[1:])       
        
    def read(self, fname) -> pd.DataFrame:
        slines = []
        spoints = []
        fromchans = []
        tochans = []
        rlines = []
        fromrecs = []
        torecs = []        
        if super().read(fname):
            with open(fname) as souf:
                for file_line in souf:
                    if file_line[0] == 'X' or self.all_lines:    
                        if self.sline_pos[1] > self.sline_pos[0]:
                            slines.append(parse_number(file_line[self.sline_pos[0]-1:self.sline_pos[1]]))
                        if self.spoint_pos[1] > self.spoint_pos[0]:    
                            spoints.append(parse_number(file_line[self.spoint_pos[0]-1:self.spoint_pos[1]]))
                        if self.fromch_pos[1] > self.fromch_pos[0]:
                            fromchans.append(parse_number(file_line[self.fromch_pos[0]-1: self.fromch_pos[1]]))
                        if self.toch_pos[1] > self.toch_pos[0]:
                            tochans.append(parse_number(file_line[self.toch_pos[0]-1: self.toch_pos[1]]))
                        if self.rline_pos[1] > self.rline_pos[0]:
                            rlines.append(parse_number(file_line[self.rline_pos[0]-1: self.rline_pos[1]]))    
                        if self.fromrec_pos[1] > self.fromrec_pos[0]:
                            fromrecs.append(parse_number(file_line[self.fromrec_pos[0]-1: self.fromrec_pos[1]]))
                        if self.torec_pos[1] > self.torec_pos[0]:    
                            torecs.append(parse_number(file_line[self.torec_pos[0]-1:self.torec_pos[1]]))                      
        else:
            return None
        return pd.DataFrame({'SLine': slines, 'SPoint': spoints, 'FromChan': fromchans, 'ToChan': tochans, 'RLine': rlines, 'FromRec': fromrecs, 'ToRec': torecs})
              
def get_pattern_by_source_coords(sx : int, sy : int, source_df : pd.DataFrame, rec_df : pd.DataFrame, pattern_df : pd.DataFrame) -> pd.DataFrame:
    line, station = source_df[(source_df.X == sx) & (source_df.Y == sy)][['Line', 'Point']].values[0]  
    pat = pattern_df[(pattern_df['SLine'] == line) & (pattern_df['SPoint'] == station)].reset_index(drop=True)
    print(pat)
    pattern_receivers = pd.DataFrame(columns=rec_df.columns)
    for i, row in pat.iterrows():
        pattern_receivers = pd.concat([pattern_receivers, rec_df[(rec_df.Line == row['RLine']) & (rec_df.Point >= row['FromRec']) & (rec_df.Point <= row['ToRec'])].reset_index(drop=True)])     

    return pattern_receivers.reset_index(drop=True)

