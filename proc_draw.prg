*IF NOT "PROC_DRAW" $ SET("PROCEDURE")  &&Added for when Quotes is run without ERP menu.
*	SET PROCEDURE TO Progs\Proc_Draw ADDITIVE
*ENDIF

************************************************************************

*Metals Handbook V14 Forming ang Forging

*Wire, Rod, and Tube Drawing

***********************************
PROCEDURE Delta_Tilda(nApproach_Semiangle_Rad, nRA )

*Delta ~ ( approach_semiangle_rad / draw_redution)[1 + (1-draw_redution_^.5]^2
*approach_semiangle in radians greek symbol is alpha
*draw_redution = 1 - (Af/Ao) = 1 - (Df^2/Do^2).   Do=3, Df=2, then 1- (2*2/3*3) = 1-(4/9) = 1-.44 = .55 
*Reduction of Area =  (Do*Do - Df*Df) / (Do*Do).                        (9-4)/9 = 5/9 = .55
*A is area = 3.14 * (D^2)/4
PRIVATE nDelta
nDelta = (nApproach_Semiangle_Rad / nRA)*( 1+ (nRA^.5) )^2
*SemiAngles in the range 6 to 10deg and draw reductions of nRA about 20% have a Delta of 2 - 3.
*nAlphaRad = AlphaRad(nDegAngle)  *Returns the degree angle to Radian. nAlphaRad = AlphaRad(6) to nAlphaRad = AlphaRad(10) 

*nAlphaRad6 = AlphaRad(6)  = .104718667
*nAlphaRad10 = AlphaRad(10) = .174531111
*nDelta6 = (.104718667/ .20)*( 1+ (.2^.5) )^2 = 1.0966
*nDelta10= (.174531111/ .20)*( 1+ (.2^.5) )^2 = 1.8277

RETURN nDelta
ENDPROC

*low Delta values may involvle excessive frictinal work.
*High Delta values involve redundant work,  
***********************************
PROCEDURE Min_DrawStress_Tilda( nCoF, nRA )
*nCoF coefficent of friction
*nRA = Reduction of Area
PRIVATE nMin_DrawStress
nMin_DrawStress = 4.9 *( nCoF / LOG(1/1-nRA) )^.5
RETURN nMin_DrawStress
ENDPROC

***********************************
PROCEDURE DrawStress_Tilda( nAve_Strength, nDelta, nApproach_Semiangle_Rad, nCoF )
*nAve_Strength of wire = flow stress of wire during the draw pass.
*nCoF coefficent of friction greek sybmol is mu
*nApproach_Semiangle_Rad greek symbal is alpha
*nDrawStress greek symbal is sigma_d
PRIVATE nDrawStress
nDrawStress = nAve_Strength*(3.2 /(nDelta +0.9)) * (nApproach_Semiangle_Rad +  nCoF )
RETURN nDrawStress
ENDPROC

***********************************
PROCEDURE Redundant_Work_Factor_Tilda( nDelta)
*nDelta
*nRedundant_Work_Factor greek symbal is Phi
PRIVATE nRedundant_Work_Factor
nRedundant_Work_Factor = (nDelta/6) +1
RETURN nRedundant_Work_Factor
ENDPROC

*Additional heat generation is associated with frictional work
*Heat can lead to lubriction breakdown.
*If the coefficient of friction is not influenced by Delta, frictional heating is aagravated by low Delta processing.
*Low approach angles (thus low Delta), foster hydrodynamic lubrication and a reduced Coefficint of Friction.
***********************************
PROCEDURE Heat_Generation( nRedundant_Work_Factor, nAve_Strength, nRA, nCapactity ,nDensity )
*nRedundant_Work_Factor greek symbal is Phi
*nAve_Strength of wire = flow stress of wire during the draw pass.
*nCapactity is Heat Capacity
*nDensity greek symbal is rho
PRIVATE nAdiabatic
nAdiabatic =  nRedundant_Work_Factor * nAve_Strength * LOG(1/1-nRA) / (nCapactity * nDensity)
RETURN nAdiabatic
ENDPROC

************************************************************************
*Volume = A*L and Ao*Lo = Af*Lf		pg367
*Engineering Strain is the greek symbol ?e?
*The strain produced in the deformation process is described by the engineering strain.
PROCEDURE Engineering_Strain_A(Ao, Af)
*Ao is Area orig
*Af is Area final
PRIVATE nEngineering_Strain
nEngineering_Strain = (Ao - Af) /Af
RETURN nEngineering_Strain
ENDPROC

************************************************************************
PROCEDURE Engineering_Strain_L(Lo, Lf)
*The strain produced in the deformation process is described by the engineering strain.
*Lo is Length orig
*Lf is Length final
PRIVATE nEngineering_Strain
nEngineering_Strain = (Lf - Lo) /Lo
RETURN nEngineering_Strain
ENDPROC

************************************************************************
*True Strain is the Greek symbol epsilon
PROCEDURE True_Strain_L(Lo, Lf)
*The strain produced in the deformation process is described by the engineering strain.
*Lo is Length orig
*Lf is Length final
PRIVATE nTrue_Strain
nTrue_Strain = LOG(Lf/Lo)
RETURN nTrue_Strain
ENDPROC

************************************************************************
PROCEDURE True_Strain_A(Ao, Af)
*True Strain is the greek symbol epsilon
*Ao is Area orig
*Af is Area final
PRIVATE nTrue_Strain
nTrue_Strain = LOG(Ao/Af)
RETURN nTrue_Strain
ENDPROC

************************************************************************
PROCEDURE True_Strain_e(nEngineering_Strain)
*The strain produced in the deformation process is described by the engineering strain.
*True Strain is the greek symbol epsilon
PRIVATE nTrue_Strain
nTrue_Strain = LOG(nEngineering_Strain + 1)
RETURN nTrue_Strain
ENDPROC

************************************************************************
PROCEDURE True_Strain_RA(nRA)
*True Strain is the greek symbol epsilon
PRIVATE nTrue_Strain
nTrue_Strain = LOG( 1/(1 - nRA) )
RETURN nTrue_Strain
ENDPROC

************************************************************************
PROCEDURE Strain_Rate(nVelocity, nCylinderHeight)
*Strain Rate is the greek symbol epsilon with a dot on top
*Strain Rate is the time rate of change of strain, the rate at which deformation proceeds.
*nVelocity in Time
*nCylinderHeight Upset in compression
PRIVATE nStrain_Rate
nStrain_Rate = nVelocity / nCylinderHeight
RETURN nStrain_Rate
ENDPROC

************************************************************************
PROCEDURE Strain_Rate_E(nTrue_Strain, nTime)
*Strain Rate is the greek symbol epsilon with a dot on top
*Strain Rate is the time rate of change of strain, the rate at which deformation proceeds. 

*True Strain is the greek symbol epsilon
*nVelocity in Time
PRIVATE nStrain_Rate
nStrain_Rate = ( nTrue_Strain / nTime)
RETURN nStrain_Rate
ENDPROC

** In most hot working, the strain hardening and the distorted grain structure 
* produced by deformation are eliminated rapidly by the formation of new strain-free grains 
* as a result of recrystallization durein or immediately after deformatin.
************************************************************************

** Friction makes the deformation more inhomeogenous, increaseing the perpensity for fracture. pg368
************************************************************************
PROCEDURE Coulomb_CoF(nShear_Stress, nStressPressure)
*Shear Stress at the interface greek symbol tau i
*nStress Pressure normal to the interface
PRIVATE nCoF
nCoF = nShear_Stress / nStressPressure
RETURN nCoF
ENDPROC

************************************************************************
PROCEDURE Shear_Stress_Interface(nConstantofProportionanality,nFlow_Stress)
*Shear Stress at the interface greek symbol tau i
*nConstantofProportionanalitycondition of lubrication and temperature, given die and material  pg368
* 0 is perfect sliding, 1 no slide
* nFlow_Stress is greek symbol sigma
PRIVATE nShear_Stress_Interface
nShear_Stress_Interface = nConstantofProportionanality * ( nFlow_Stress / SQRT(3) )
RETURN nShear_Stress_Interface
ENDPROC

***********************************
PROCEDURE Uniaxial_Compressive_Stress(nPForce, nArea)
*Uniaxial_Compressive_Stress is flow stress, only true if there is no friction   pg 376
*nForce
*nArea
PRIVATE nFlow_Stress
nFlow_Stress = (nPForce / nArea)
RETURN nFlow_Stress
ENDPROC

***********************************
PROCEDURE True_Compresive_Strain(nHeight_o, nHeight_f)
*True_Compresive_Strain is greek symbol epsilon
*Buckeling will occure if nHeight/Diameter > 2
PRIVATE nTrue_Compresive_Strain
nTrue_Compresive_Strain = LOG( nHeight_o / nHeight_f )
RETURN nTrue_Compresive_Strain
ENDPROC

***********************************
PROCEDURE True_Compressive_Stress(nPForce, nHeight_o, nHeight_f, nDia
*True_Compressive_Stress
PRIVATE nTrue_Compressive_Stress
nTrue_Compressive_Stress = (4* nPForce * nHeight_f) / (3.14156 * nDia * nDia * nHeight_o )
RETURN nTrue_Compressive_Stress
ENDPROC

************************************************************************
*Wire Technology
*Process Engineering and Metallurgy
*by Roger N. Wright


*What is nStress


***********************************
PROCEDURE Reduction_of_Area( Ao, A1 )
*gamma
*Returns as fraction
PRIVATE nRA
IF Ao*A1 = 0
	nRA = 0
ELSE
	nRA = (Ao-A1)/Ao
ENDIF
*nRA = 1-(A1/Ao)
*percent reduction	[(Ao-A1)/Ao]*100
RETURN nRA
ENDPROC

***********************************
PROCEDURE Reduction_of_Area_D( Do, D1 )
PRIVATE nRA	&&gamma
*Returns fraction
* commercial practice rarely involves reductions above 30%
* use *100 for Percentage
IF Do*D1 = 0
	nRA = 0
ELSE
	nRA = ((Do*Do) - (D1*D1))/(Do*Do)
ENDIF

RETURN nRA
ENDPROC


***********************************
PROCEDURE AlphaRad(nDegAngle)
*Returns the degree angle to Radian
PRIVATE nAlphaRad
nAlphaRad = (nDegAngle/360)*(2*3.14156)
RETURN nAlphaRad
ENDPROC


***********************************
PROCEDURE DegreeAngle(nAlphaRad)
*Return the Degree Angle from Alpha Radians
PRIVATE nDegreeAngle
nDegreeAngle = nAlphaRad*180/3.14156
RETURN nDegreeAngle
ENDPROC

***********************************
PROCEDURE Deformation_Zone(nAlphaRad,nRA)
*Returns Delta
*deformation zone	 the ratio of Angle / reduction of area
PRIVATE nDelta 
nDelta = ( nAlphaRad/nRA)*(1+(1-nRA)^.5 ) ^2
*also can use for deformation zone
*nDelta = 4 * TAN( nRad)/ LN( 1/(1-nRA) )

*!*	Delta above 1.3 the centerline hydrostatic stress is tensile
*!*	 higher die angles result in increased values of centerline tension 
*!*	 for higher ? values, plastic deformation occurs both upstream and downstream from this nominal deformation zone
*!*	redundant work increase substantially as Delta increases.

*!*	function of reduction and die angle
*!*	 die designs involving low Delta values (i.e., low approach angles and/or large reductions)
*!*	 should offer superior performance in terms of reduced wear, reduced requirements for intermediate annealing
*!*	 reduced cuppy core breakage, improved final product ductility, and minimization of thinning beyond the die exit.
*!*	Delta above 1.3, the centerline hydrostatic stress is tensile
*!*	 low Delta die design fosters relatively uniform metal flow with reduced redundant work

RETURN nDelta 
ENDPROC


***********************************
PROCEDURE deform_zone_length_Rad(do, d1, nRad )
*length of deform zone	Ld	(do-d1)/(2 TAN( nRad ))
PRIVATE nLd
nLd = (do-d1)/(2 * TAN( nRad ))
RETURN nLd
ENDPROC


***********************************
PROCEDURE die_contact_length_Rad(do, d1, nRad )
*Die contact length		Lc	(do-d1)/(2 SIN( nRad ))
PRIVATE nLc
nLc = (do-d1)/(2 * SIN( nRad ))
RETURN nLc
ENDPROC



***********************************
PROCEDURE drawing_stress( nPull_force, nA1 )
*sigma_d	Pulling force / A1
PRIVATE sigma_d
sigma_d = nPull_force * nA1
RETURN sigma_d
ENDPROC


***********************************
PROCEDURE back_stress( nBack_force, nA0 )
*Back stress	 		sigma_b	back force / A0
PRIVATE sigma_b
sigma_b = nBack_force / nA0
RETURN sigma_b
ENDPROC


***********************************
*PROCEDURE die_pressure( )
*P	 average die pressure acting upon the wire in the deformation zone
*sophisticated drawing analyses indicate that the pressure is not uniform 
* but higher near the drawing channel entrance and exit and lower in between.
*PRIVATE nP
*nP = 0
*RETURN nP
*ENDPROC
	 		

***********************************
PROCEDURE draw_work(nForce, nLength)
*Returns Work
*Work=Force*length 		W = F * L
PRIVATE nWork
nWork = nForce * nLength
RETURN nWork
ENDPROC

*!*	work /volume = force / area


*!*						mu = coefficient of friction
*!*						
*!*						
*!*	*		 the role of higher die angles in increasing Delta.
*!*	Centerline stress	 sigma_m	 mean normal stress at the centerline, particularly at the point where sigma_m has the most tensile
*!*			 great concern in drawing because they can lead to fracture at the wire center.
*!*	 hydrostatic cl stress	sigma_m	 Above a Delta value of about 1.3, sigma_m becomes increasingly tensile




***********************************
PROCEDURE draw_force(nDrawStress, nArea1)
*Return Force using Orig Area --Same as draw_work
* F = draw stress * A1
PRIVATE nDrawForce
nDrawForce = nDrawStress * nArea1
RETURN nDrawForce
ENDPROC

***********************************
PROCEDURE draw_work(nDrawStress, nArea1)
*Return Force using Orig Area  --Sames as draw_force
* Force = DrawForce = draw stress * A1
PRIVATE nDrawForce
nDrawForce = nDrawStress * nArea1
RETURN nDrawForce
ENDPROC

***********************************
PROCEDURE draw_stress_volume(nDraw_Work, nVolume)
*Retuns DrawStress using Volume
*!*	draw stress is sigma_d	 work divided by volume
PRIVATE nDrawStress
nDrawStress = nDraw_Work / nVolume
RETURN nDrawStress
ENDPROC

***********************************
PROCEDURE draw_stress_Area(nDraw_Force, nArea1)
*Retuns DrawStress using Orig Area
*!*	draw stress	sigma_d	Force / Area = F/A1 or W/(L*A1)
PRIVATE nDrawStress
nDrawStress = nDraw_Force/ nArea1
RETURN nDrawStress
ENDPROC


***********************************
PROCEDURE draw_stress_Pull_Back(nPull_Force, nArea1, nBackForce, nArea0)
*Returns Pull Back DrawStress using Change of Area
*!*	 drawing stress	=	Pull Force/A1 + Back Force/A0
PRIVATE nDrawStress
nDrawStress = (nPull_Force/ nArea1)+ (nBackForce/ nArea0)
RETURN nDrawStress
ENDPROC

***********************************
PROCEDURE draw_stress_Work(nWu, nWr, nWf)
*!*	draw stress	sigma_d	is Work = (Wu + Wr + Wf)
PRIVATE nDrawStress
nDrawStress = nWu + nWr + nWf
RETURN nDrawStress
ENDPROC


***********************************
PROCEDURE work_uniform(nWork, nArea)
*!*	work uniform	Wu	work per unit volume
PRIVATE nWork
nWork = nWork / nArea
RETURN nWork
ENDPROC

***********************************
PROCEDURE work_uniform_stress(nStress, nArea0, nArea1)
*!*		Wu	avg flow stress*LN(Ao/A1)
PRIVATE nWork
nWork = nStress * Log( nArea0/ nArea1 )
RETURN nWork
ENDPROC


***********************************
PROCEDURE work_uniform_stress2(nStress, nRA)
*		Wu	sigma_a * LN( 1/(1-RA) )
*		it should be understood that the flow stress can be expected to increase from die entry to die exit due to strain hardening.
PRIVATE nWork
nWork = nStress * LOG(1/(1-nRA))
RETURN nWork
ENDPROC


***********************************
PROCEDURE work_redundant(nWork, nArea)
*	Wr	Redundant stress - The perpindiculat strain that is die pressure with no net effect.
*!*	redundant work	Wr	related work that does not cancel.  This work divided by volume
*!*	redundant work increase substantially as Delta increases.
PRIVATE nWork
nWork = (nWork / nArea)
RETURN nWork
ENDPROC


***********************************
PROCEDURE work_friction(nWork, nArea)
*!*	friction work	Wf	friction
PRIVATE nFrictionWork
nFrictionWork = (nWork / nArea)
RETURN nFrictionWork
ENDPROC


***********************************
PROCEDURE drawing_stress_ratio(nDraw_Stress, nAve_Stress)
*	drawing stress ratio	Sigma = sigma_d / sigma_a
*where is nDraw_Stress or nAve_Stress found
PRIVATE nStress_Ratio
nStress_Ratio = (nDraw_Stress / nAve_Stress)
RETURN nStress_Ratio
ENDPROC


***********************************
PROCEDURE redundant_work_factor_Work(nWu,nWr)
*!*	 redundant work factor	Phi
*!*	Phi = 1 when there is NO redundant work
*!*	redundant work factor		(Wu + Wr) / Wu
PRIVATE nPhi
nPhi = (nWu + nWr) / nWu
RETURN nPhi
ENDPROC

***********************************
PROCEDURE work_redundant_factor_Phi(nPhi,nStress,nRA)
PRIVATE nWork
*!*	redundant work	Wr	(? -1)Wu
*!*		Wr	(Phi -1)* sigma *LN(1/(1-nRA))
nWork = (nPhi - 1) *nStress *LOG(1/(1-nRA))
RETURN nWork
ENDPROC

***********************************
PROCEDURE redundant_work_factor_Dia(nDia,nLength_Contact)
*!*	 redundant work factor	Phi
*!*	Phi = 0.88 + 0.12* (nDia /nLength_Contact)
PRIVATE nPhi
nPhi = 0.88 + ( 0.12 * (nDia /nLength_Contact) )
RETURN nPhi
ENDPROC

***********************************
PROCEDURE redundant_work_factor_Delta(nDeformationZone)
*!*	 redundant work factor,	Phi, the Ratio of total deformation work / deformation work implied by diminsional change
*!*	Phi = 0.8+  ( Delta*4.4)									5.8
PRIVATE nPhi
nPhi = 0.88 + ( nDeformationZone * 4.4 )
RETURN nPhi
ENDPROC


***********************************
PROCEDURE die_pressure(nPhi,nAve_Stress)
PRIVATE nDieP 
*!*	Avg die pressure	P	Phi * sigma_a	
*aka redundant work factor * draw stress
*!*		die pressure reflects redundant and uniform work
nDieP = (nPhi * nAve_Stress)
RETURN nDieP 
ENDPROC


***********************************
PROCEDURE redundant_work_factor_RA(nCoF,nRad,nRA)
*!*	 redundant work factor	Phi
*!*	Wf	= mu * 1/TAN( nRad) * LN(1/(1-nRA))
PRIVATE nWorkR
nWorkR = nCoF * (1/TAN( nRad)) * LOG(1/(1-nRA) )
RETURN nWorkR
ENDPROC

***********************************
PROCEDURE redundant_work_factor_Stress(nCoF, nPhi, nAve_Stress, nDelta)
*!*	 redundant work factor	Phi
*!*	Wf	= 4 mu Phi sigma_a/ Delta
PRIVATE nWorkR
nWorkR = 4 *nCoF * nPhi * ( nAve_Stress / nDelta)
RETURN nWorkR
ENDPROC


***********************************
PROCEDURE coefficient_of_friction(nSigma_d, nSigma_a, nDelta, nRad )
*!*	coefficient of friction	mu = (sigma_d/sigma_a) ((3.2/ Delta)+.9)^-1  -nRad		8.4
PRIVATE nCOF
nCOF = ((nSigma_d/nSigma_a)* ((3.2/ nDelta)+.9)^-1) -nRad	
RETURN nCOF
ENDPROC


***********************************
PROCEDURE work_friction_RA(nCoF, nRAD, nPhi, nSigma_a, nDelta, nRA )
*!*	frictional work	Wf	mu COT(nRad) Phi sigma_a * LN(1/(1-nRA))		5.9
*!*		friction on bearing or land does not count!
*!*		
*!*		Issues of Optimum Die Angle and Delta
*!*		Redundant Work (thus drawing stress) increase as Delta increase
*!*		Friction Work (thus drawing stress) decrease as Delta increases
PRIVATE nWF
nWF = nCoF * (COS(nRad)/SIN(nRAD)) * nPhi *nSigma_a * Log(1/(1-nRA))
RETURN nWF
ENDPROC



***********************************
PROCEDURE work_friction(nCoF, nPhi, nSigma_a, nDelta, nRA )
*!*		Wf	4*CoF*Phi * sigma_a / Delta		5.10
*!*		friction on bearing or land does not count!
*!*		
*!*		Issues of Optimum Die Angle and Delta
*!*		Redundant Work (thus drawing stress) increase as Delta increase
*!*		Friction Work (thus drawing stress) decrease as Delta increases
PRIVATE nWF
nWF = 4*nCoF*nPhi*(nSigma_a/nDelta)
RETURN nWF
ENDPROC

***********************************
PROCEDURE drawing stress(nSigma_a, nRA, nPhi, nCOF, nRadian, nDelta )

*nSigma_a is
*sigma_d is Drawing Stress
*!*	sigma_d	= sigma_a * LN(1/(1-nRA)) + (Phi-1) mu COT(nRad) * sigma_a * LN(1/(1-nRA)) + 4 mu * Phi * sigma_a /Delta
*!*		drawing stress must remain below the flow stress at the die exit
PRIVATE nDrawStress
nDrawStress = nSigma_a * ( LN(1/(1-nRA)) + (nPhi-1) * nCoF * COT(nRadian) * sigma_a * LN(1/(1-nRA)) )+ (4*nCoF * nPhi * nSigma_a / nDelta)
RETURN nDrawStress
ENDPROC

***********************************
PROCEDURE drawing_stress_ratio_Stress(nSigma_d, nSigma_a)
*!*	drawing stress ratio	sigma_d/sigma_a	=(4Phi/Delta) (nRad+mu)
PRIVATE nStressRatio
nStressRatio = (nSigma_d / nSigma_a )
RETURN nStressRatio
ENDPROC

***********************************
PROCEDURE drawing_stress_ratio_Phi(nPhi,nDelta,nRadian,nCoF))
*!*	drawing stress ratio	(4Phi/Delta) (nRad+CoF)
PRIVATE nStressRatio
nStressRatio = (4 * nPhi/nDelta) * (nRadian+nCoF)
RETURN nStressRatio
ENDPROC

***********************************
PROCEDURE drawing_stress_ratio_Delta(nDelta,nRadian,nCoF)
*!*	drawing stress ratio	Sigma = [(3.2/Delta ) + 0.9]  (nRad + CoF)
PRIVATE nStressRatio
nStressRatio = ((3.2/nDelta) +0.9) + (nRadian + nCoF)
RETURN nStressRatio
ENDPROC


***********************************
PROCEDURE drawing_limit(nSigma_d,nSigma_a)
*!*	Drawing limit	Sigma	drawing limit is Sigma = 1
*nSigma_d = delta draw stress 
*nSigma_a = delta ave flow stress
*!*	Sigma =	sigma_d/sigma_a		delta draw stress / delta ave flow stress		
PRIVATE nSigma
nSigma = (nSigma_d/nSigma_a)
RETURN nSigma
ENDPROC

***********************************
PROCEDURE drawing_limit_Rad(nDelta, nRad, nCoF)
*!*	Sigma = sigma_d/sigma_a		=[( 3.2/ Delta )+0.9] (nRad+CoF)
PRIVATE nSigma
nSigma = (( 3.2/ nDelta )+0.9) * (nRad+nCoF)
RETURN nSigma
ENDPROC

***********************************
PROCEDURE drawing_limit_RA(nDelta, nRA, nCoF)
*Retuns Drawing limit
*!*	Sigma = sigma_d/sigma_a	=  [( 3.2/ Delta )+0.9]*[Delta*nRA* [1+ (1-nRa) ^.5 ]^-2 +mu]
PRIVATE nSigma
nSigma = (( 3.2/ nDelta )+0.9)*(nDelta*nRA* (1+ (1-nRa) ^.5 )^-2) +nCoF
RETURN nSigma
ENDPROC

*!*	 Optimum Die Angles and Delta Values
***********************************
PROCEDURE delta_optimum(nCoF,nRA)
*!*	Delta optimum	Delta_opt	= (1.89)( mu/nRa  )^.5 [1+(1 - nRa)^.5 ]
PRIVATE nDelta_opt
nDelta_opt = 1.89*(nCoF / nRa)^.5 *(1+(1 - nRA)^.5 )
RETURN nDelta_opt 
ENDPROC

***********************************
PROCEDURE angle_optimum(nCoF,nRa)
*!*	Angle optimum	Angle_opt	= (1.89)(  mu*nRa )^.5 [1+(1 - nRA)^.5 ] 5.16
PRIVATE nAngle_opt
nAngle_opt = 1.89*(nCoF * nRa)^.5 * (1+(1 - nRA)^.5 )
RETURN nAngle_opt
ENDPROC


***
***********************************
PROCEDURE average_die_pressure(nWu,nWr)
*!*	Average die pressure	P	= Wu+Wr uniform and redundant work
PRIVATE nAveDiePressure
nAveDiePressure= nWu + nWr
RETURN nAveDiePressure
ENDPROC

***********************************
PROCEDURE Ratio_DieP_over_nSigma_a(nP,nSigma_a)
*!*	Ave press/Ave flow stress	= P/sigma_a	= Delta/4 + .06
PRIVATE nRatio
nRatio = nP/nSigma_a
RETURN nRatio
ENDPROC

*!*	High levels of friction will, however, substantially decrease die pressure.
*!*	Centerline tension in drawing is of great concern because it promotes the development and growth of porosity and ductile fracture of the wire at the centerline
*!*	The average stress at the centerline is less compressive than at the die wall and may evenbe tensile. This is particularly the case for higher values of ?.

***********************************
PROCEDURE Ratio_DieP_over_nSigma_a(nDelta)
*!*	Ave press/Ave flow stress	= P/sigma_a	= Delta/4 + .06
PRIVATE nRatio
nRatio = ( nDelta/4 ) + .06
RETURN nRatio
ENDPROC




*!*	Ave friction stress						
*!*	back tension	sigma_d	= sigma_do + sigma_ab (in the absence of friction)				5.19

***********************************
PROCEDURE sigma_d(nSigma_a, nSigma_b, nDelta,nRad,nCoF, nRad, nRA)
*Return Back Tension, sigma_d
*!*					sigma_d	= sigma_a[ (3.2/Delta) + .09]( nRad+CoF ) + sigma_b[ 1- ( CoF*nRa / nRad )(1 - nRA)^-1 ]				5.20
PRIVATE nSigma_d, nPreSigma, nPreSigma_b
nPreSigma_a = ((3.2/nDelta) + .09)*( nRad+nCoF ) 
nPreSigma_b = ( 1- ( nCoF*nRA / nRad ) * (1 - nRA)*SqRt(-1) )
nSigma_d = (nSigma_a*nPreSigma) + ( nSigma_b*nPreSigma_b )
RETURN nSigma_d
ENDPROC

***********************************
PROCEDURE avg_die_pressure(nSigma_d,nSigma_a)
*!*	Avg die pressure, back tension	Po	Avg die pressure in the absence of back tension and b = sigma_d/sigma_a	
PRIVATE nAveDieP
nAveDieP = nSigma_d/nSigma_a
RETURN nAveDieP
ENDPROC

***********************************
PROCEDURE back_tension(nSigma_d,nSigma_a)
*!*	back tension b = sigma_d/sigma_a	
PRIVATE nBackTension
nBackTension = nSigma_d/nSigma_a
RETURN nBackTension
ENDPROC

*!*		P /Po	= 1 - [2b/(2-Sigma)]	


***********************************
PROCEDURE drawing_stress_ratio(nSigma_d,nSigma_a)
*!*	Sigma	= sigma_d/sigma_a	drawing stress ratio
PRIVATE nDrawStressRatio
nDrawStressRatio = nSigma_d/nSigma_a
RETURN nDrawStressRatio
ENDPROC

*!*	***********************************
*!*	PROCEDURE drawing_stress(nT0, nVolume  )
*!*	*!*	ave flow stress	Sigma 	 through two dies in tandem, the draw stress for the initial die constitutes a back stress for the final die	
*!*	*!*	 just prior to die entry	T0	Temperature
*!*	*!*	 work per unit volume	w	is equivalent to the drawing stress, sigma_d
*!*	*!*	drawing stress	sigma_d	
*!*	PRIVATE nSigma_d
*!*	nSigma_d

*!*	RETURN nSigma_d
*!*	ENDPROC

***********************************
PROCEDURE equilibrated_temperature(nT0, nSigma_d, nC, nDensity)	)
*!*			 the wire will be hotter at the surface than at the center.				
*!*	 equilibrated temperature	Teq	T0  + sigma_d/ (C*rho)				6.1
*!*		C is specific heat of the wire				
*!*		rho	is density of the wire		
PRIVATE nEquilibrated_Temperature
nEquilibrated_Temperature = nT0 + (nSigma_d / ( nC * nDensity ) )
RETURN nEquilibrated_Temperature
ENDPROC



***********************************
PROCEDURE adiabatic_heat(nSigma_d, nSpecificHeat, nDensity)
*!*	adiabatic heat = sigma_d/ (C*rho)				
*!*		nSpecificHeat, C is specific heat of the wire				
*!*		nDensity, rho	is density of the wire		
PRIVATE nAdiabaticHeat
nAdiabaticHeat = (nSigma_d /(nSpecificHeat * nDensity))
RETURN nAdiabaticHeat
ENDPROC
		
***********************************
PROCEDURE length_equilibrium(nVelocity, nSpecificHeat, nDensity, nDia, nK)
*!*	Length equilibrium	Leq	(velocity *C*rho dia^2) /(24K)				6.2
*!*		nSpecificHeat, C is specific heat of the wire				
*!*		nDensity, rho	is density of the wire		
*!*		K	 thermal conductivity				
PRIVATE nLengthEquilibrium
nLengthEquilibrium = (nVelocity * nSpecificHeat * nDensity * nDia*nDia) /(24*nK)
RETURN nLengthEquilibrium
ENDPROC


***********************************
PROCEDURE uniform_work(nSigma_a, nRa, nSpecificHeat, nDensity))
*!*	uniform work	Tuw	 adiabatic drawing temperature increase associated with uniform work				
*!*		Tuw = sigma_a * LN( 1/(1-nRa) )/ (C*rho)				6.3
PRIVATE nWu
nWu = nSigma_a * LOG( 1/(1-nRa) ) / (nSpecificHeat * nDensity)
RETURN nWu 
ENDPROC

***********************************
PROCEDURE redundant_work(nDelta, nSigma_a, nRA, nSpecificHeat, nDensity) )
*!*	 redundant work	= Trw = (Delta-1) sigma_a * LN( 1/(1-nRa) )/ (C*rho)				6.4
PRIVATE nRedundantWork
nRedundantWork = (nDelta-1) * nSigma_a * LOG( 1/(1-nRa) ) / (nSpecificHeat * nDensity)
RETURN nRedundantWork
ENDPROC

***********************************
PROCEDURE wire_temperature(nDelta, nSigma_a, nRA, nSpecificHeat, nDensity) 
*!*	 total contribution	Tw = Delta sigma_a * LN( 1/(1-nRa) )/ (C*rho)				6.5
*!*	wire temperature	Tw															???
PRIVATE nWireTemperature
nWireTemperature = nDelta * nSigma_a * LOG( 1/(1-nRa) )/ (nSpecificHeat * nDensity)
RETURN nWireTemperature
ENDPROC

***********************************
PROCEDURE AngleInRadians(nAngleInDegrees)
PRIVATE nAngleInRadians 
nAngleInRadians = DTOR( nAngleInDegrees )
RETURN nAngleInRadians 
ENDPROC
***********************************
PROCEDURE AngleInDegrees(nAngleInRadians)
PRIVATE nAngleInDegrees
nAngleInDegrees = RTOD( nAngleInRadians )
RETURN nAngleInDegrees
ENDPROC


***********************************
PROCEDURE friction_temperature(nCoF, nRad, nDelta, nSigma_a, nRA, nSpecificHeat, nDensity  )
*!*	 adiabatic drawing temperature increase associated with friction work
*!*	friction temperature	Tf = CoF* COT(nRad) Delta * sigma_a * LN( 1/(1-nRA) )/ (C*rho)
PRIVATE nFrictionTemperature
nFrictionTemperature = nCoF * ATAN(nRad) * nDelta * nSigma_a * LOG( 1/(1-nRA) ) / (nSpecificHeat * nDensity)
RETURN nFrictionTemperature
ENDPROC

***********************************
PROCEDURE frictional_heating(nCoF, nDelta, nSigma_a, nVelocity, nLd, nSpecificHeat, nDensity, nK)
*!*	 frictional heating		 (1.25) * CoF * Delta * sigma_a * [(velocity * Ld)/(C * rho * K)]^.5
PRIVATE nFrictionalHeating
nFrictionalHeating = 1.25 * nCoF * nDelta * nSigma_a *  ((nVelocity * nLd) / (nSpecificHeat * nDensity * nK))^.5
RETURN nFrictionalHeating
ENDPROC

***********************************
PROCEDURE adiabatic_temp_increase(nDelta, nSigma_a, nRA, nSpecificHeat, nDensity )
*!*	adiabatic temp increase	 DeltaTd = Delta * sigma_a *LN(1/1-nRA)/ C*rho
PRIVATE nAdiabaticTempIncrease
nAdiabaticTempIncrease  = nDelta * nSigma_a * LOG(1/1-nRA) / (nSpecificHeat * nDensity )
RETURN nAdiabaticTempIncrease
ENDPROC



***********************************
PROCEDURE wire_surface_temperature_die_exit(nCoF, nDelta, nSigma_a, nv, nLd, nSpecificHeat, nDensity, nK, nT0)
*!*	Tmax	 wire surface temperature at the die exit
*!*	Tmax	(1.25) CoF * Delta * sigma_a *((vLd)/(C rho K))^.5 + Delta *sigma_a * LN( 1/(1-nRa) )/ (C rho)  +T0
*!*	v	 drawing speed

PRIVATE nWireSurfaceTemperatureDieExit, nWireT1, nWireT2
nWireT1 = 1.25 * nCoF * nDelta * nSigma_a *((nv * nLd) / (nSpecificHeat * nDensity * nK))^.5
nWireT2 = nDelta * nSigma_a * LOG(1/1-nRA) / (nSpecificHeat * nDensity )
nWireSurfaceTemperatureDieExit = nWireT1 + nWireT2 + nT0
RETURN nWireSurfaceTemperatureDieExit
ENDPROC


*!*		
*!*	mu=nCoF	The coefficients of friction in drawing with oil-based lubricants directly reflect the viscosities of the lubricants
*!*		 frictional stresses increase with increasing viscosity in the functional temperature range of the lubricant
*!*		
*!*		Frictional stresses with solid soap lubrication most directly reflect the shear strengths of the lubricants
*!*		 increases in temperature during drawing may be beneficial as well as detrimental



*!*			Drawing Speed Ch7				
*!*	Drawing Speed		Practical drawing speeds range from 10 to 5000 m/min.				

***********************************
PROCEDURE velocity_in(nVelocityOut, nArea0, nArea1  )
*!*	 volume does not change	V0 A0	= V1 A1				7.1
*!*	 wire velocity	V 
PRIVATE nVelocityIn
nVelocityIn = nVelocityOut * nArea0/ nArea1
RETURN nVelocityIn
ENDPROC

***********************************
PROCEDURE velocity_out(nVelocityIn, nArea0, nArea1  )
*!*	 volume does not change	V0 A0	= V1 A1				7.1
*!*	 wire velocity	V 
PRIVATE nVelocityOut
nVelocityOut = nVelocityIn * nArea0/ nArea1
RETURN nVelocityOut
ENDPROC

***********************************
PROCEDURE area_out(nVelocityIn, nVelocityOut, nAreaOrig  )
*!*		A0/A1	= V1/V0				7.2
*!*		A0	= (V1/V0)A1 
*!*		A1 = A0	/ (V1/V0)
PRIVATE nAreaFinal
nAreaFinal = nAreaOrig / (nVelocityIn/nVelocityOut)
RETURN nAreaFinal
ENDPROC

***********************************
PROCEDURE area_start(nVelocityOut, nVelocityOut, nAreaOut )
*!*		A0/A1	= V1/V0				7.2
*!*		A0 = V1/V0 * A1			
PRIVATE nAreaIn
nAreaIn = ( nVelocityIn/nVelocityOut) * nAreaOut
RETURN nAreaIn
ENDPROC

***********************************
PROCEDURE pulling_speed(nVelocityOut, nDiameter, nRPM)
*!*	pulling speed	V1 = 3.14 * D * rpm 				7.3
*!*	diameter	D	diameter of bar, rod or wire				
*!*	rpm	block speed in revolution per unit time				
PRIVATE nPullingSpeed
nPullingSpeed = nVelocityOut *3.14 * nDiameter * nRPM
RETURN nPullingSpeed
ENDPROC

***********************************
PROCEDURE power(nDrawForce,  nVelocityOut)
*!*	 power = F * V1	 drawing force times the exit speed	
*!*	power		newton meter per second = joules persecond = watts				
*!*		F	force in Newtons				
			
PRIVATE nPower
nPower = nDrawForce * nVelocityOut
RETURN nPower
ENDPROC
					

*!*							


***********************************
PROCEDURE true_strain_rate(nD_Epsilon_t, ndt)
*!*	 true strain rate	 d_epsilon_t/dt	 since strain is dimensionless, the units of strain rate are s? 1		
PRIVATE nTrue_Strain_Rate
nTrue_Strain_Rate = (nD_Epsilon_t / ndt )
RETURN nTrue_Strain_Rate
ENDPROC


***********************************
PROCEDURE average_strain_rate_V(nEpsilon_t, nV0, nV1, nLd)
*!*	average strain rate	 d_epsilon_t/dt	= epsilon_t *(V0+V1) / (2Ld)				7.4
*!*		Ld	length of the deformation zone				
PRIVATE nAverage_Strain_Rate
nAverage_Strain_Rate = nEpsilon_t * (nV0 + nV1) / (2*nLd)
RETURN nAverage_Strain_Rate
ENDPROC
		
***********************************
PROCEDURE frictional_heating(nCoF, nDelta, nSigma_a, nv, nLd, nC, nrho, nK)
*!*	 frictional heating		 (1.25)CoF * Delta * sigma_a *[(v * Ld)/(C * rho * K)]^.5	
*!*		v drawing speed	
*!*		Ld	length of the deformation zone	
PRIVATE nFrictional_Heating
nFrictional_Heating = (1.25) * nCoF * nDelta * nSigma_a * ((nv * nLd)/(nC * nrho * nK))^.5				
RETURN nFrictional_Heating
ENDPROC


***********************************
*PROCEDURE ()
*PRIVATE
*RETURN 
*ENDPROC

*!*	  equilibration temperature
*!*	Leq	= (v C*rho d^2) /(24K)
*!*	Teq	= Leq/ v = (C*rho* d^2) /(24K)
*!*	Teq	= (1 + mu COT(nRad)) Delta * sigma_a * LN( 1/(1-nRa) )/ (C rho) +To
*!*	Teq	= T0 + sigma_d/(Crho)

*!*	increased drawing speed can increase drawing temperature
*!*	eta	is lubricant viscosity
*!*	eta * v/P	lubricant film thickness increases with the index (eta v/P)
*!*	drawing speed	v	
*!*	die pressure	P	

***********************************
PROCEDURE redundant_work_factor_1(nDelta)
*!*	redundant work factor is Theta
*!*	Theta = ratio of total deformation work to the deformation work implied by dimensional change
*!*	Theta = 0.8 + ( Delta /4.4)
*!*	Theta = (Delta/6) + 1
*!*		 Relatively sharp blends are recommended for the drawing of high carbon steel and stainless steel
*!*		 A blend likely exposes the last stages of the drawing pass to the conditions of a lower die angle and thus a lower ?
*!*		This should reduce redundant work, die pressure, and centerline tension at the end of the pass.
*!*		This can be a big factor in the case of light passes, where the nominal, overall ? may be uncomfortably large

PRIVATE nRedundant_Work_Factor
nRedundant_Work_Factor = 0.8 + ( nDelta /4.4)
RETURN 
ENDPROC

***********************************
PROCEDURE redundant_work_factor_2(nDelta)
*!*	redundant work factor is Theta
*!*	Theta = ratio of total deformation work to the deformation work implied by dimensional change
*!*	Theta = 0.8 + ( Delta /4.4)
*!*	Theta = (Delta/6) + 1
*!*		 Relatively sharp blends are recommended for the drawing of high carbon steel and stainless steel
*!*		 A blend likely exposes the last stages of the drawing pass to the conditions of a lower die angle and thus a lower ?
*!*		This should reduce redundant work, die pressure, and centerline tension at the end of the pass.
*!*		This can be a big factor in the case of light passes, where the nominal, overall ? may be uncomfortably large

PRIVATE nRedundant_Work_Factor
nRedundant_Work_Factor = (nDelta/6) + 1
RETURN 
ENDPROC
***********************************
*PROCEDURE ( ,  )
*PRIVATE
*RETURN 
*ENDPROC

*!*			 Archard equation, is widely used for general analysis of wear behavior:				
*!*			Vwear / Lsliding = qF/H				9.1
*!*		Vwear	the volume of material worn away				
*!*		Lsliding	the distance of sliding	Length of wire			
*!*		F	Force				
*!*		H 	Hardness				
*!*		 q	proportion constant				
*!*	delta = average die diameter increase due to wear.				
*!*	(not sigma)	delta = P(2 Lsliding q /H)				9.2
*!*	 Lsliding		(H delta)/(2qP)				9.3
*!*	t life		(H delta)/(2vqP)				9.4
***********************************
*PROCEDURE ( ,  )
*PRIVATE
*RETURN 
*ENDPROC

*!*		v	drawing speed				
*!*	Mass	M	( 3.14/4)Lsliding Pd^2				9.5
*!*		p	wire density				
*!*		d	as-drawn wire diameter			
***********************************
*PROCEDURE ( ,  )
*PRIVATE
*RETURN 
*ENDPROC
	
*!*	t life		Qd / (vP)				9.6
*!*	constant	Qd	(H delta)/(2q)				
*!*							
*!*	Poor lubrication nearly always leads to shortened die life.				
*!*	Die wear will generally be increased by increased die pressure, as caused by lighter reductions, higher die angles, higher Delta values, and higher wire flow stress.
***********************************
*PROCEDURE ( ,  )
*PRIVATE
*RETURN 
*ENDPROC

*!*					
*!*	To divide up a sequence of passes from A0 to A1 into n equal area reductions, true strain must be calculated				

*!*		 rn	1- EXP( - epslion * tn )				

***********************************
PROCEDURE die_angle(nRA, nDelta)
*!*	die angle	alpha = gamma(1+(1-gamma)^.5) ^-2  * Delta				9.7
*nRA = Gamma
PRIVATE nDie_Angle
nDie_Angle = (nRA(1+(nRA)^.5) ^-2)  * nDelta
RETURN nDie_Angle
ENDPROC

***********************************
PROCEDURE true_strain(nAo,nA1)
*!*	True strain	= epsilon_t = LN(Ao/A1)				
PRIVATE nEpsilon_t
nEpsilon_t = LOG(nAo/nA1)
RETURN nEpsilon_t
ENDPROC

***********************************
PROCEDURE draw_stress_delta(nSigma_a, nDelta, nAlpha, nMu )
*!*	Pass schedules designed for maximum reduction in each pass should involve a constant ratio of draw stress				
*!*	draw stress	sigma_d = sigma_a * [(3.2/Delta ) + 0.9]  (alpha + mu)  	=	sigma_a * Sigma		5.13
*!*	Sigma = sigma_d / sigma_a				
PRIVATE nSigma_d
nSigma_d = nSigma_a * ((3.2/nDelta ) + 0.9) * (nAlpha + nMu)
RETURN nSigma_d
ENDPROC

***********************************
PROCEDURE draw_stress_sigma_d(nSigma_a, nSigma)
*!*	Pass schedules designed for maximum reduction in each pass should involve a constant ratio of draw stress				
*!*	draw stress	sigma_d = sigma_a * [(3.2/Delta ) + 0.9]  (alpha + mu)  	=	sigma_a * Sigma		5.13
*!*	Sigma = sigma_d / sigma_a				
PRIVATE nSigma_d
nSigma_d = nSigma_a * nSigma	
RETURN nSigma_d
ENDPROC

***********************************
PROCEDURE sigma(nSigma_a, nSigma_d)
*!*	Sigma = sigma_d / sigma_a				
PRIVATE nSigma
nSigma = nSigma_d / nSigma_a
RETURN nSigma
ENDPROC

***********************************
PROCEDURE work_hardening(nK, nTrue_Strain, nWork_hardening_Exponent)
*!*	sigma_0 = K * epsilon ^n  for room temp work-hardening	
*!*	sigma_0	representing strength or true flow stress 

*!*	epsilon	as true strain, true_strain(nAo,nA1)	
*!*	K	 strength coefficient	
*!*	n 	work-hardening exponent	
PRIVATE nWork_Hardening
nWork_Hardening = (nK * nTrue_Strain) ^nWork_hardening_Exponent
RETURN nWork_Hardening
ENDPROC


	

*!*	
***********************************
*PROCEDURE ()
*PRIVATE
*RETURN 
*ENDPROC
				
*!*	High Delta drawing, leading to greater degrees of redundant work and a greater potential for nonuniformity.
*!*	Worn dies, since wear and the related interference with lubrication may not be circumferentially uniform
*!*	Die misalignment, including intentional misalignments to create cast.
*!*	Misalignments of the “wire route” with the die holder (influences of capstans, guides, etc.).
*!*	Dies drilled off center, or with asymmetric blends.
*!*	Vibrations along the wire route.

*!*	 A light reduction may be associated with a high Delta value. 
*!*	 Equation (5.18) indicates that an increased Delta value will increase die pressure, which in turn should increase die wear
***********************************
*PROCEDURE ()
*PRIVATE
*RETURN 
*ENDPROC


*********************************** PROCEDURE ()PRIVATE RETURN ENDPROC
*********************************** 
PROCEDURE Area_hollow (nOD, nID)
PRIVATE nArea
nArea = 3.14156/4 * ((nOD*nOD)-(nID*nID))
RETURN nArea
ENDPROC

*********************************** 
PROCEDURE Reduction_of_Area_hollow (nOrig_OD, nOrig_ID, nFinal_OD, nFinal_ID )
PRIVATE nRA
nRA = (((nOrig_OD*nOrig_OD)-(nOrig_ID*nOrig_ID)) - ((nFinal_OD*nFinal_OD)-(nFinal_ID*nFinal_ID ))) / ((nOrig_OD*nOrig_OD)-(nOrig_ID*nOrig_ID))
RETURN nRA
ENDPROC

