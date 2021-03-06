import unittest
import numpy as n
import useful_functions as uf 
import Q_gsm_error_analysis as qgea

# python test_qgea.py TestRecoverGS.test_recover_diag

class TestRecoverGS(unittest.TestCase):
    def test_recover_diag(self):
        Q = n.diag(n.arange(1,9)[::-1])
        N = n.identity(8)
        a = n.arange(2,17,2)
        #a = a[::-1]
        y = n.dot(Q,a)#+uf.rand_from_covar(N)
        a,ahat,err = qgea.test_recover_alms(y,Q,N,a,num_remov=3)
        print "diag"
        print a
        print ahat
        self.assertTrue(n.allclose(a[:-3],ahat[:-3]))
        self.assertTrue(n.allclose(0,ahat[-3:]))

    def test_recover_wind(self):
        print "Window"
        num=100
        Q = n.diag(n.arange(1,9))
        N = n.identity(8)
        a = n.arange(2,17,2)
        a1 = n.arange(2,17,2)
        ahat_avg = 0
        for ii in range(num):
            n_vec = uf.rand_from_covar(N)
            Qa = uf.vdot(Q,a)
            y = Qa+n_vec
            self.assertTrue(y.shape==(8,))
            a,ahat,err = qgea.test_recover_alms(y,Q,N,a,num_remov=-4)        
            ahat_avg += ahat
            self.assertTrue(n.all(y==n.dot(Q,a1)+n_vec))
        ahat_avg = ahat_avg/num
        W = qgea.window_fn_matrix(Q,N,num_remov=-4)
        print uf.vdot(W,a)
        print ahat_avg
        self.assertTrue(n.all(n.abs(n.dot(W,a)-ahat_avg)<0.1))

    def test_subtract_noise(self):
        Q = n.diag(n.arange(1,9))
        N = n.identity(8)
        a = n.arange(2,17,2)
        n_vec = uf.rand_from_covar(N)
        Qa = uf.vdot(Q,a)
        y = Qa+n_vec
        a,ahat,err = qgea.test_recover_alms(y,Q,N,a,num_remov=-4) 
        _,nhat,err = qgea.test_recover_alms(n_vec,Q,N,a,num_remov=-4) 
        ahat_better = ahat - nhat
        W = qgea.window_fn_matrix(Q,N,num_remov=-4)
        self.assertTrue(n.allclose(n.dot(W,a),ahat_better))

    def test_recover_gs(self):
        print "GS"
        num=500
        Q = n.diag(n.arange(1,9))
        N = n.identity(8)*50
        N[0,0]=1
        a = n.array([16,0,0,0,0,0,0,0])#n.arange(16,1,-2)
        print 'a ',a 
        ahat_avg = 0
        for ii in range(num):
            n_vec = uf.rand_from_covar(N)
            Qa = uf.vdot(Q,a)
            y = Qa+n_vec
            self.assertTrue(y.shape==(8,))
            a,ahat,err = qgea.test_recover_alms(y,Q,N,a,num_remov=0)        
            ahat_avg += ahat
        ahat_avg = ahat_avg/num
        W = qgea.window_fn_matrix(Q,N,num_remov=0)

        print uf.vdot(W,a)
        print ahat_avg
        self.assertTrue(n.abs(uf.vdot(W,a)[0]-ahat_avg[0])<0.1)
        #self.assertTrue(n.all(n.abs(n.dot(W,a)-ahat_avg)<0.2))

    def test_recover_gs_ratio(self):
        print "GS Ratio"
        Q = n.diag(n.arange(1,9))
        N = n.identity(8)*50
        #N[0,0]=1
        a = n.array([16,4,0,0,0,0,0,0])#n.arange(16,1,-2)
        print 'a ',a 
        n_vec = uf.rand_from_covar(N)
        Qa = uf.vdot(Q,a)
        y = Qa+n_vec
        self.assertTrue(y.shape==(8,))
        a,ahat,err = qgea.test_recover_alms(y,Q,N,a,num_remov=0)        
        W = qgea.window_fn_matrix(Q,N,num_remov=0)
        Wa = uf.vdot(W,a)
        print 'Wa ',Wa
        print 'ahat ',ahat
        print Wa[0]/Wa[1]
        print a[0]/a[1]
        self.assertTrue(n.abs(Wa[0]/Wa[1]-a[0]/a[1])<0.1)    

    def test_sum(self):
        N = n.identity(8)
        Q = n.identity(8)
        Q[0,3] = 1; Q[3,0] = 1
        a = n.arange(8); a[0] = 10
        y = uf.vdot(Q,a)
        a,ahat,err = qgea.test_recover_alms(y,Q,N,a,num_remov=1) 
        W = qgea.window_fn_matrix(Q,N,num_remov=1)
        Wa = uf.vdot(W,a)
        print 'Wa ',Wa
        print 'ahat ',ahat
        print Wa[0]/Wa[1]
        print a[0]/a[1]
        self.assertAlmostEqual(ahat[0],(a[0]+a[3])/2.)
        self.assertAlmostEqual(ahat[3],(a[0]+a[3])/2.)
        self.assertTrue(n.allclose(Wa,ahat))



if __name__=='__main__':
    unittest.main()
