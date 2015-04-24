import numpy as np
from normalvectors import PanelVectors, PointVectors
from InfForce import Transformation

# neutral axis is the axis which coincides with the chord line and divides the 
# symmetric airfoil into two.        
def NeutralAxis(Body,x_ref,dstep,tstep,t):
# uses Body.(theta_max, f, phi)
# returns x_neut, z_neut (just pitching for now)
    
    # pitching motion of the airfoil(x and z points of the neutral axis due to pitching motion)
    x_neut_p=(x_ref+dstep)*np.cos(Body.theta_max*np.sin(2*np.pi*Body.f*(t+tstep) + Body.phi))
    z_neut_p=(x_ref+dstep)*np.sin(Body.theta_max*np.sin(2*np.pi*Body.f*(t+tstep) + Body.phi))

    # heaving motion of the airfoil(x and z points of the neutral axis due to the heaving motion)
    # xneuth = xref+dstep
    # zneuth = Body.h_c*Body.c*np.sin(2*np.pi*Body.f*(t+tstep))*np.ones(len(xref))
    
    # burst and coast behaviour of the airfoil
    ####################

    # overall neutral axis position
    return(x_neut_p,z_neut_p)
    
# gets the panel endpoint positions and collocation point positions of the body
def PanelPositions(Body,S,dstep,t):
# uses NeutralAxis()
# uses Body.(x, z, z_col, V0)
# gets Body.(X, Z, X_col, Z_col)
# others: xneut, zneut, xdp_s, zdp_s, xdm_s, zdm_s
    
    # Body Surface Panel Endpoint Calculations
    (xneut,zneut)=NeutralAxis(Body,Body.x,0,0,t)
    
    # infinitesimal differences on the neutral axis to calculate the tangential and normal vectors
    (xdp_s,zdp_s)=NeutralAxis(Body,Body.x,dstep,0,t)
    (xdm_s,zdm_s)=NeutralAxis(Body,Body.x,-dstep,0,t)
    
    # displaced airfoil's surface points for time t0
    Body.X = xneut + PointVectors(xdp_s,xdm_s,zdp_s,zdm_s)[2]*Body.z + Body.V0*t
    Body.Z = zneut + PointVectors(xdp_s,xdm_s,zdp_s,zdm_s)[3]*Body.z
    
    # collocation points are the points where impermeable boundary condition is forced
    # they should be shifted inside or outside of the boundary depending on the dirichlet or neumann condition
    # shifting surface collocation points some percent of the height from the neutral axis
    # normal vectors point outward but positive S is inward, so the shift must be subtracted from the panel midpoints
    Body.X_col = (Body.X[1:]+Body.X[:-1])/2 - S*PanelVectors(Body.X,Body.Z)[2]*np.absolute(Body.z_col)
    Body.Z_col = (Body.Z[1:]+Body.Z[:-1])/2 - S*PanelVectors(Body.X,Body.Z)[3]*np.absolute(Body.z_col)
    
# this method calculates the actual surface positions of the airfoil for each time step
# using the neutral axis and appropriate normal vectors of each point on the neutral axis
# this class also calculates the velocity of the panel midpoints for each time step
def SurfaceKinematics(Body,dstep,tstep,t):
# uses NeutralAxis(), PointVectors()
# uses Body.(x_col, z_col, V0)
# gets Body.(Vx, Vz)
# others: xtpneut, ztpneut, xtpdp, ztpdp, xtpdm, ztpdm, xtmneut, ztmneut, xtmdp, ztmdp, xtmdm, ztmdm, xctp, xctm, zctp, zctm
    
    # Panel Midpoint Velocity Calculations
    # calculating the surface positions at tplus(tp) and tminus(tm) for every timestep
    (xtpneut,ztpneut)=NeutralAxis(Body,Body.x_col,0,tstep,t)
    (xtpdp,ztpdp)=NeutralAxis(Body,Body.x_col,dstep,tstep,t)
    (xtpdm,ztpdm)=NeutralAxis(Body,Body.x_col,-dstep,tstep,t)
    (xtmneut,ztmneut)=NeutralAxis(Body,Body.x_col,0,-tstep,t)
    (xtmdp,ztmdp)=NeutralAxis(Body,Body.x_col,dstep,-tstep,t)
    (xtmdm,ztmdm)=NeutralAxis(Body,Body.x_col,-dstep,-tstep,t)
    
    # displaced airfoil's panel midpoints for times tplus(tp) and tminus(tm)      
    xctp = xtpneut + PointVectors(xtpdp,xtpdm,ztpdp,ztpdm)[2]*Body.z_col + Body.V0*t
    xctm = xtmneut + PointVectors(xtmdp,xtmdm,ztmdp,ztmdm)[2]*Body.z_col + Body.V0*t
        
    zctp = ztpneut + PointVectors(xtpdp,xtpdm,ztpdp,ztpdm)[3]*Body.z_col
    zctm = ztmneut + PointVectors(xtmdp,xtmdm,ztmdp,ztmdm)[3]*Body.z_col
    
    # velocity calculations on the surface panel midpoints
    Body.Vx = (xctp - xctm)/(2*tstep)
    Body.Vz = (zctp - zctm)/(2*tstep)
    
def EdgeShed(Body,Edge,i,delt):
# uses Body.(X, Z, x_neut, z_neut, V0) and Edge.Ce
# gets Edge.(X, Z)
# others: none
    
    if i==0:
        pass
    
    # the trailing edge panel whose length can be varied to optimize the solution
    else:
        Edge.X[0] = Body.X[0]
        Edge.Z[0] = Body.Z[0]
        Edge.X[1] = Body.X[0] + Edge.Ce*PanelVectors(Body.x_neut,Body.z_neut)[0][0]*Body.V0*delt
        Edge.Z[1] = Body.Z[0] + Edge.Ce*PanelVectors(Body.x_neut,Body.z_neut)[1][0]*Body.V0*delt
    
# wake position calculations
def WakeShed(Edge,Wake,i,delt):
# uses Edge.(X, Z, mu) and Wake.(X, Z, V0, mu)
# gets Wake.(X, Z, mu, gamma)
# others: none
    
    # first timestep is before t=0(geometry initialization timestep)
    if i==0:
        pass
    
    # initialize wake coordinates when i==1
    elif i==1:
        
        Wake.X[0] = Edge.X[-1]
        Wake.Z[0] = Edge.Z[-1]
        
        Wake.X[1:] = Wake.X[0] + np.arange(1,np.size(Wake.X))*(-Wake.V0)*delt
        Wake.Z[1:] = Wake.Z[0]
    
    else:
        Wake.X[1:] = Wake.X[:-1]
        Wake.Z[1:] = Wake.Z[:-1]
        Wake.mu[1:]= Wake.mu[:-1]
        
        Wake.X[0] = Edge.X[-1]
        Wake.Z[0] = Edge.Z[-1]
        Wake.mu[0]= Edge.mu
        
        Wake.gamma[0]=-Wake.mu[0]
        Wake.gamma[1:-1]=Wake.mu[:-1]-Wake.mu[1:]
        Wake.gamma[-1]=Wake.mu[-1]

def WakeRollup(Body,Edge,Wake,delta_core,i,delt):
# uses Transformation
# uses Body.(X, Z, gamma, N, sigma)
# uses Edge.(X, Z, gamma, N)
# uses Wake.(X, Z, gamma)
# gets Wake.(X, Z)
# others: Xpleft, Xpright, Zp, nx, nz, beta, junk1, junk2, junk3, junk4, Xp, Zp, r_b, r_e, r_w, Vx, Vz
    
    # wake panels (not including the trailing edge panel) initialize when i==2
    if i<2:
        pass
    
    else:
        
        Nt = i-1 # number of targets (wake panel points that are rolling up)
        
        Vx=np.zeros(Nt)
        Vz=np.zeros(Nt)
        
        # coordinate transformation for body panels influencing wake
        (Xpleft,Xpright,Zp)=Transformation(Wake.X[1:i],Wake.Z[1:i],Body.X,Body.Z)
        
        # angle of normal vector with respect to global z-axis
        (nx,nz)=PanelVectors(Body.X,Body.Z)[2:4]
        beta = np.arctan2(-nx,nz)
        
        # Katz-Plotkin eqns 10.20 and 10.21 for body source influence
        junk1=np.transpose( np.log((Xpleft**2+Zp**2)/(Xpright**2+Zp**2))/(4*np.pi) )
        junk2=np.transpose( (np.arctan2(Zp,Xpright)-np.arctan2(Zp,Xpleft))/(2*np.pi) )
        
        # rotate back to global coordinates
        junk3=junk1*np.cos(beta) - junk2*np.sin(beta)
        junk4=junk1*np.sin(beta) + junk2*np.cos(beta)
        
        # finish eqns 10.20 and 10.21 for induced velocity by multiplying with Body.sigma
        Vx=np.dot(junk3,Body.sigma)
        Vz=np.dot(junk4,Body.sigma)
        
        # formation of (x-x0) and (z-z0) matrices, similar to Xpleft/Xpright/Zp but coordinate transformation is not necessary
        Ni=Body.N+1
        Xp=np.repeat(Wake.X[1:i,np.newaxis].T,Ni,0) - np.repeat(Body.X[:,np.newaxis],Nt,1)
        Zp=np.repeat(Wake.Z[1:i,np.newaxis].T,Ni,0) - np.repeat(Body.Z[:,np.newaxis],Nt,1)
        
        # find distance r_b between each influence/target
        r_b=np.sqrt(Xp**2+Zp**2)
        
        # Katz-Plotkin eqns 10.9 and 10.10 for body doublet (represented as point vortices) influence
        junk1=np.transpose(Zp/(2*np.pi*(r_b**2+delta_core**2)))
        junk2=np.transpose(-Xp/(2*np.pi*(r_b**2+delta_core**2)))
        
        # finish eqns 10.9 and 10.10 by multiplying with Body.gamma, add to induced velocity
        Vx+=np.dot(junk1,Body.gamma)
        Vz+=np.dot(junk2,Body.gamma)
        
        # formation of (x-x0) and (z-z0) matrices, similar to Xpleft/Xpright/Zp but coordinate transformation is not necessary
        Ni=Edge.N+1
        Xp=np.repeat(Wake.X[1:i,np.newaxis].T,Ni,0) - np.repeat(Edge.X[:,np.newaxis],Nt,1)
        Zp=np.repeat(Wake.Z[1:i,np.newaxis].T,Ni,0) - np.repeat(Edge.Z[:,np.newaxis],Nt,1)
        
        # find distance r_e between each influence/target
        r_e=np.sqrt(Xp**2+Zp**2)
        
        # Katz-Plotkin eqns 10.9 and 10.10 for edge (as point vortices) influence
        junk1=np.transpose(Zp/(2*np.pi*(r_e**2+delta_core**2)))
        junk2=np.transpose(-Xp/(2*np.pi*(r_e**2+delta_core**2)))
        
        # finish eqns 10.9 and 10.10 by multiplying with Edge.gamma, add to induced velocity
        Vx+=np.dot(junk1,Edge.gamma)
        Vz+=np.dot(junk2,Edge.gamma)
        
        # formation of (x-x0) and (z-z0) matrices, similar to Xpleft/Xpright/Zp but coordinate transformation is not necessary
        Ni=i
        Xp=np.repeat(Wake.X[1:i,np.newaxis].T,Ni,0) - np.repeat(Wake.X[:i,np.newaxis],Nt,1)
        Zp=np.repeat(Wake.Z[1:i,np.newaxis].T,Ni,0) - np.repeat(Wake.Z[:i,np.newaxis],Nt,1)
        
        # find distance r_w between each influence/target
        r_w=np.sqrt(Xp**2+Zp**2)
        
        # Katz-Plotkin eqns 10.9 and 10.10 for wake (as point vortices) influence
        junk1=np.transpose(Zp/(2*np.pi*(r_w**2+delta_core**2)))
        junk2=np.transpose(-Xp/(2*np.pi*(r_w**2+delta_core**2)))
        
        # finish eqns 10.9 and 10.10 by multiplying with Wake.gamma, add to induced velocity
        Vx+=np.dot(junk1,Wake.gamma[:i])
        Vz+=np.dot(junk2,Wake.gamma[:i])
        
        # modify wake with the total induced velocity
        Wake.X[1:i]+=Vx*delt
        Wake.Z[1:i]+=Vz*delt