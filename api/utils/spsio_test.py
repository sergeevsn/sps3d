from spsio import SPSReceiverReader, SPSSourceReader, SPSRelationReader, REV21_REC_FORMAT, REV21_SOU_FORMAT, REV21_REL_FORMAT
from spsio import get_pattern_by_source_coords

rec_format = "LINE:2:11,POINT:12:25,X:30:37,Y:39:47,Z:49:53"
        
sou_format = "LINE:2:11,POINT:12:25,UPHOLE:27:29,DEPTH:35:36,X:42:49,Y:51:59,Z:61:65"
rel_format = "SLINE:14:17,SPOINT:34:37,FROMCH:39:43,TOCH:44:48,RLINE:48:59,FROMREC:62:71,TOREC:72:79"
r = SPSReceiverReader(REV21_REC_FORMAT)
receivers = r.read('D:/WORK/SPS/3dam08.Rsps')
s = SPSSourceReader(REV21_SOU_FORMAT)
sources = s.read('D:/WORK/SPS/3dam08.Ssps')
x = SPSRelationReader(REV21_REL_FORMAT)
relation = x.read('D:/WORK/SPS/3dam08.Xsps')



print(relation)
sx, sy = sources.iloc[100][['X', 'Y']].values
print(get_pattern_by_source_coords(sx, sy, sources, receivers, relation))