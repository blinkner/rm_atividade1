import math,unittest
from rm_atividade1.control import wrap,scan_points,corridor_clear,choose_heading
class TestControl(unittest.TestCase):
    def test_angle_crosses_pi(self):self.assertAlmostEqual(wrap(math.radians(358)),math.radians(-2))
    def test_scan_invalid_is_not_free(self):
        p,v=scan_points([math.nan,-math.inf,0,math.inf,1],0,.1,.02,12,.008)
        self.assertEqual(len(p),1);self.assertAlmostEqual(v,.4)
    def test_clear_heading(self):self.assertEqual(choose_heading([],0,.8,.3,0),0)
    def test_obstacle_in_corridor(self):
        self.assertFalse(corridor_clear([(.5,0)],0,.8,.3))
        h=choose_heading([(.5,0)],0,.8,.3,0)
        self.assertIsNotNone(h);self.assertGreater(abs(h),.5)
    def test_no_turn_inside_obstacle_margin(self):self.assertIsNone(choose_heading([(.1,0)],0,.8,.3,0))
    def test_endpoint_margin(self):self.assertFalse(corridor_clear([(.9,0)],0,.8,.3))
if __name__=='__main__':unittest.main()
