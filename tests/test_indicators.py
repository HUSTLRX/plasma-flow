import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('node'), 'Node needed for isolated geometry tests')
class WidgetGeometryTests(unittest.TestCase):
    def geometry(self, radius):
        directory=ROOT/'package/contents/ui/common'
        geometry='\n'.join(line for line in (directory/'IndicatorGeometry.js').read_text().splitlines() if not line.startswith('.'))
        setup="var IndicatorStyles={EdgeLine:0,SideLine:1,Block:2,Rounded:3,FullSize:4,UseLabels:5};"
        args={'style':3,'config':{'LabelStyle':5,'NoneIndicatorWidth':32,'NoneIndicatorHeight':8,'NoneIndicatorRadius':radius},
              'parentWidth':37,'parentHeight':36,'isVertical':False,'isTopLocation':True,'usesLabelMetrics':False}
        program=setup+geometry+';console.log(JSON.stringify(computeGeometry('+json.dumps(args)+')));'
        return json.loads(subprocess.check_output(['node','-e',program],text=True))
    def test_reference_label_free_geometry(self):
        self.assertEqual(self.geometry(4),{'w':32,'h':8,'x':2.5,'y':14,'r':4})
    def test_radius_stays_within_indicator(self):
        self.assertEqual(self.geometry(100)['r'],4)

if __name__=='__main__':unittest.main()
