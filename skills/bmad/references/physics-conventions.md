# Bmad Physics Conventions Reference

## Table of Contents

1. [Coordinate Systems](#coordinate-systems)
   - [Global (Floor) Coordinates](#global-floor-coordinates)
   - [Laboratory (Local) Coordinates](#laboratory-local-coordinates)
   - [Element Body Coordinates](#element-body-coordinates)
   - [Coordinate Transformations Between Frames](#coordinate-transformations-between-frames)
2. [Reference Orbit Construction](#reference-orbit-construction)
3. [Phase Space Coordinates](#phase-space-coordinates)
   - [Charged Particle Phase Space](#charged-particle-phase-space)
   - [The z Coordinate and Time](#the-z-coordinate-and-time)
   - [Momentum Coordinates](#momentum-coordinates)
   - [Photon Phase Space](#photon-phase-space)
   - [MAD vs Bmad Conventions](#mad-vs-bmad-conventions)
4. [Electromagnetic Field Conventions](#electromagnetic-field-conventions)
   - [Magnetic Multipole Expansion](#magnetic-multipole-expansion)
   - [Normal and Skew Components](#normal-and-skew-components)
   - [Multipole Scaling](#multipole-scaling)
   - [Electrostatic Multipole Fields](#electrostatic-multipole-fields)
   - [Exact Multipoles in a Bend](#exact-multipoles-in-a-bend)
   - [Field Maps](#field-maps)
5. [Fringe Field Models](#fringe-field-models)
   - [Hard Edge vs Soft Edge](#hard-edge-vs-soft-edge)
   - [Bend Fringe Fields](#bend-fringe-fields)
   - [Quadrupole Soft Edge Fringe](#quadrupole-soft-edge-fringe)
   - [RF Fringe Fields](#rf-fringe-fields)
6. [Linear Optics](#linear-optics)
   - [Coupling and Normal Modes](#coupling-and-normal-modes)
   - [Twiss Parameters](#twiss-parameters)
   - [Dispersion](#dispersion)
   - [Tunes and Eigen Analysis](#tunes-and-eigen-analysis)
   - [Action-Angle Coordinates](#action-angle-coordinates)
7. [Synchrotron Radiation](#synchrotron-radiation)
   - [Radiation Damping and Excitation](#radiation-damping-and-excitation)
   - [Synchrotron Radiation Integrals](#synchrotron-radiation-integrals)
   - [Equilibrium Emittance](#equilibrium-emittance)
8. [Wakefields](#wakefields)
   - [Short-Range Wakes](#short-range-wakes)
   - [Long-Range Wakes](#long-range-wakes)
9. [Spin Dynamics](#spin-dynamics)
10. [Multiparticle Simulation](#multiparticle-simulation)
    - [Bunch Distributions](#bunch-distributions)

---

## Coordinate Systems

Bmad uses three coordinate systems: global (floor), laboratory (local), and element body.

### Global (Floor) Coordinates

The global coordinate system is the fixed Cartesian frame attached to the building/earth. Axes are labeled $(X, Y, Z)$ where $Y$ is vertical and $(X, Z)$ are horizontal.

A point on the reference orbit is described by position vector $\mathbf{V} = (X, Y, Z)^T$ and orientation matrix $\mathbf{W}$ whose columns are the unit vectors of the local $(x, y, z)$ axes. The orientation is parameterized by three Tait-Bryan angles (not Euler):

- $\theta(s)$ -- **Azimuth (yaw)**: angle in the $(X, Z)$ plane between $Z$-axis and projection of local $z$-axis. Positive $\theta = \pi/2$ means $z$ points along $+X$.
- $\phi(s)$ -- **Pitch (elevation)**: angle between local $z$-axis and the $(X, Z)$ plane. Positive $\phi = \pi/2$ means $z$ points along $+Y$.
- $\psi(s)$ -- **Roll**: angle of local $x$-axis relative to the intersection of $(X, Z)$ with $(x, y)$ planes.

The $\mathbf{W}$ matrix is:

$$\mathbf{W} = \mathbf{R}_y(\theta) \; \mathbf{R}_{-x}(\phi) \; \mathbf{R}_z(\psi)$$

By default at $s = 0$, the local axes coincide with the global axes.

### Laboratory (Local) Coordinates

The local curvilinear coordinate system follows the bends of the accelerator. A particle's position is described by the point $\mathcal{O}$ on the reference orbit at longitudinal position $s$, plus transverse offsets $(x, y)$. The local $z$-axis is tangent to the reference orbit and, by construction, a particle is always at $z = 0$ in the local frame (do not confuse with phase space $z$).

The curvature vector $\mathbf{g}$ lies in the $x$-$y$ plane with magnitude $1/\rho$ where $\rho$ is the bending radius.

### Element Body Coordinates

Element body coordinates are attached to the physical element. Without misalignments (offsets, pitches, tilt), they coincide with laboratory coordinates. With misalignments, a transformation is needed.

For **straight elements**, the lab-to-body transformation goes through the element center:

$$\mathbf{L} = (\text{x\_offset}, \text{y\_offset}, \text{z\_offset})^T$$
$$\mathbf{S} = \mathbf{R}_y(\text{x\_pitch}) \; \mathbf{R}_{-x}(\text{y\_pitch}) \; \mathbf{R}_z(\text{tilt})$$

For **bend elements**, the transformation is more complex because `ref_tilt` is defined at the bend entrance while offsets/pitches/roll are defined at the center. Five sequential transformations are needed.

### Coordinate Transformations Between Frames

Element positioning uses iterative equations:

$$\mathbf{V}_i = \mathbf{W}_{i-1} \; \mathbf{L}_i + \mathbf{V}_{i-1}$$
$$\mathbf{W}_i = \mathbf{W}_{i-1} \; \mathbf{S}_i$$

For straight elements: $\mathbf{L} = (0, 0, L)^T$, $\mathbf{S} = \mathbf{I}$.

For bends with `ref_tilt` angle $\theta_t$ and bend angle $\alpha_b$:

$$\mathbf{L} = \mathbf{R}_z(\theta_t) \; (\rho(\cos\alpha_b - 1), \; 0, \; \rho\sin\alpha_b)^T$$

To transform a point $\mathbf{Q}_g$ from global to a local frame $(\mathbf{V}, \mathbf{W})$:

$$\mathbf{Q}_{VW} = \mathbf{W}^{-1}(\mathbf{Q}_g - \mathbf{V})$$

---

## Reference Orbit Construction

The reference orbit is the curved path defining the local coordinate system. It is constructed by concatenating elements like "LEGO blocks," each with an entrance and exit coordinate frame.

- **Straight elements**: entrance and exit frames are colinear.
- **Bend elements**: frames are rotated by the bend angle.
- **Patch/floor_shift elements**: exit frame can be arbitrarily positioned.

Construction starts at `beginning_ele` and proceeds by mating the downstream frame of one element to the upstream frame of the next. An element's upstream end is normally its entrance end, but for **reversed elements** the exit end becomes upstream (requiring a reflection patch between reversed and unreversed elements).

---

## Phase Space Coordinates

### Charged Particle Phase Space

Bmad uses canonical phase space coordinates:

$$\mathbf{r}(s) = (x, p_x, y, p_y, z, p_z)$$

The independent variable is the longitudinal position $s$ (not time). The transverse positions $x$ and $y$ are independent of the reference particle position.

### The z Coordinate and Time

The phase space $z$ is defined as:

$$z(s) = -\beta(s) \, c \, (t(s) - t_0(s)) \equiv -\beta(s) \, c \, \Delta t(s)$$

where $t(s)$ is the particle arrival time at position $s$, $t_0(s)$ is the reference particle arrival time, and $\beta = v/c$. Positive $z$ means the particle is ahead of the reference particle.

At constant velocity equal to the reference velocity:

$$\Delta z = L_0 - L_p$$

where $L_0$ is the reference path length and $L_p$ is the actual particle path length.

Propagation of $z$ between two points:

$$z_2 = \frac{\beta_2}{\beta_1} z_1 - \beta_2 \, c \, (\Delta t_2 - \Delta t_1)$$

Note: if $\beta$ is discontinuous (e.g., instantaneous kick), $z$ is also discontinuous.

### Momentum Coordinates

The transverse momenta are normalized by the reference momentum $P_0$:

$$p_x = P_x / P_0, \qquad p_y = P_y / P_0$$

The longitudinal momentum:

$$p_z = \Delta P / P_0 = (P - P_0) / P_0$$

The relationship between momenta and slopes $x' = dx/ds$, $y' = dy/ds$:

$$x' = \frac{p_x}{\sqrt{(1+p_z)^2 - p_x^2 - p_y^2}} (1 + g\,x)$$

with $g = 1/\rho$ being the curvature. A similar equation holds for $y'$.

### Photon Phase Space

Photons use a different phase space:

$$\mathbf{r} = (x, \beta_x, y, \beta_y, z, \beta_z)$$

where $(\beta_x, \beta_y, \beta_z)$ is the normalized photon velocity with $\beta_x^2 + \beta_y^2 + \beta_z^2 = 1$, and $z$ is the distance from the start of the element. Photons also carry polarization parameters $(E_x, \phi_x, E_y, \phi_y)$.

### MAD vs Bmad Conventions

MAD replaces $(z, p_z)$ with $(\tau, p_\tau)$:

$$\tau = -c \, \Delta t = z / \beta$$
$$p_\tau = \Delta E / (P_0 c) = E/(P_0 c) - 1/\beta_0$$

The two systems are identical in the ultra-relativistic limit. Dispersion values will differ between Bmad and MAD for non-relativistic beams.

---

## Electromagnetic Field Conventions

### Magnetic Multipole Expansion

The vertical field along the $y = 0$ axis is expanded as:

$$B_y(x, 0) = \sum_n B_n \frac{x^n}{n!}$$

The normalized field strength:

$$K_n = \frac{q \, B_n}{P_0}$$

where $q$ is the reference particle charge and $P_0$ is the reference momentum (eV/c). The quantity $P_0/q$ is sometimes written as $B\rho$.

Kicks from a multipole of length $L$:

$$\Delta p_x = -K_0 L - K_1 L \, x + \tfrac{1}{2} K_2 L (y^2 - x^2) + \ldots$$
$$\Delta p_y = K_1 L \, y + K_2 L \, xy + \ldots$$

A positive $K_1 L$ gives horizontal focusing and vertical defocusing.

### Normal and Skew Components

Using the $a_n$, $b_n$ representation (normal and skew):

$$\frac{q \, L}{P_0}(B_y + i B_x) = (b_n + i a_n)(x + iy)^n$$

The conversion to/from $(K_n L, S_n L, T_n)$ (magnitude, skew, rotation angle):

$$b_n + i a_n = \frac{1}{n!}(K_n L + i S_n L) e^{-i(n+1)T_n}$$

To convert a normal magnet to skew, rotate by $(n+1)T_n = \pi/2$. For example, a normal quadrupole rotated by 45 degrees becomes a skew quadrupole.

### Multipole Scaling

**Reference energy scaling** (when `field_master = True`):

$$[a_n, b_n] \rightarrow [a_n, b_n] \cdot q / P_0$$

**Element strength scaling** (when `scale_multipoles = True`), using measurement radius $r_0$ and scale factor $F$:

$$[a_n, b_n] \rightarrow [a_n, b_n] \cdot F \cdot r_0^{n_\text{ref}} / r_0^n$$

where $F$ and $n_\text{ref}$ depend on the element type (e.g., $F = K_1 \cdot L$, $n_\text{ref} = 1$ for quadrupoles).

### Electrostatic Multipole Fields

Electric fields use normal $b_{en}$ and skew $a_{en}$ components with measurement radius `r0_elec`:

$$E_x - i E_y = (b_{en} - i a_{en}) \frac{(x + iy)^n}{r_0^n}$$

Unlike magnetic multipoles, electric components are *not* normalized by element length or reference momentum.

### Exact Multipoles in a Bend

In a curved geometry, multipole fields differ from the straight-geometry case. Fields satisfy Laplace's equation in curvilinear coordinates, leading to "vertically pure" and "horizontally pure" solutions. The `exact_multipoles` attribute of a bend controls which convention is used. Note that chromaticity from a horizontally pure quadrupole field differs from a vertically pure one of the same strength.

### Field Maps

Bmad supports three field map decompositions for parameterizing fields that satisfy Maxwell's equations:

- **Cartesian Map**: sum of Laplace solutions in Cartesian separation of variables (DC fields only). Uses families `x`, `y`, `qu`, `sq` with forms `hyper-y`, `hyper-xy`, `hyper-x`.
- **Cylindrical Map**: suitable for both DC and AC fields.
- **Generalized Gradient Map**: derived from cylindrical decomposition, expanding the scalar potential in powers of radius.

---

## Fringe Field Models

### Hard Edge vs Soft Edge

Fringe kicks are decomposed as:

```
Total fringe kick = hard edge fringe kick + soft edge fringe kick
```

The **hard edge** fringe is the kick in the limit of zero longitudinal fringe extent. The **soft edge** fringe accounts for finite longitudinal extent minus the hard edge contribution. Hard edge fringes are a good approximation in many cases without knowing the fringe field profile.

### Bend Fringe Fields

The bend hard edge fringe uses Lie map generators based on Hwang and Lee, modified to include quadrupole terms. The generator at the entrance:

$$\Omega_{M1} = \frac{(x^2 - y^2) g_\text{tot} \tan(e_1)}{2} + \frac{y^2 g_\text{tot}^2 \sec^3(e_1)[1+\sin^2(e_1)] f_\text{int} h_\text{gap}}{1+p_z} + \ldots$$

where $g_\text{tot}$ is the total bending strength, $e_1$/$e_2$ are the edge angles, $f_\text{int}$ and $h_\text{gap}$ parameterize the fringe field integral and gap.

Available dipole fringe models:
- **Second-order hard edge** (Hwang-Lee): default, includes up to second order in transverse coordinates
- **SAD soft edge**: adapted from SAD, parameterized by `fb1`/`fb2` (or `fint`/`hgap`)
- **Linear hard edge**: adapted from MAD, first-order only
- **Exact hard edge**: exact transport through the wedge region

### Quadrupole Soft Edge Fringe

Adapted from SAD, the quadrupole soft edge fringe uses parameters `fq1` and `fq2` related to field integrals:

$$g_1 = \frac{K_1 \cdot \text{fq1}}{1 + p_z}, \qquad g_2 = \frac{K_1 \cdot \text{fq2}}{1 + p_z}$$

The map includes exponential focusing/defocusing in $x$ and $y$:

$$x_2 = x_1 e^{g_1} + g_2 p_{x1}, \quad p_{x2} = p_{x1} e^{-g_1}$$

### RF Fringe Fields

Assuming cylindrical symmetry, the RF fringe kick at the entrance end:

$$\Delta p_x = -\frac{q \hat{E}_z}{2 c P_0} x$$

where $\hat{E}_z$ is the longitudinal electric field just inside the fringe. The exit-end kick is the negative of the entrance kick.

---

## Linear Optics

### Coupling and Normal Modes

The one-turn map $\mathbf{T}$ for transverse coordinates $\mathbf{x} = (x, x', y, y')$ is decomposed:

$$\mathbf{T} = \mathbf{V} \, \mathbf{U} \, \mathbf{V}^{-1}$$

where $\mathbf{U}$ is block-diagonal with $2\times 2$ blocks $\mathbf{A}$ (a-mode) and $\mathbf{B}$ (b-mode), each parameterized by standard Twiss form:

$$\mathbf{A} = \begin{pmatrix} \cos\theta_a + \alpha_a\sin\theta_a & \beta_a\sin\theta_a \\ -\gamma_a\sin\theta_a & \cos\theta_a - \alpha_a\sin\theta_a \end{pmatrix}$$

The coupling matrix $\mathbf{V}$ has the Edwards-Teng form:

$$\mathbf{V} = \begin{pmatrix} \gamma\mathbf{I} & \mathbf{C} \\ -\mathbf{C}^+ & \gamma\mathbf{I} \end{pmatrix}$$

with symplecticity condition $\gamma^2 + |\mathbf{C}| = 1$. The coupling matrix $\mathbf{C}$ is zero if and only if the motion is uncoupled.

**Mode flips** occur in highly coupled lattices where the a-mode at one location corresponds to the b-mode at another. Bmad tracks `mode_flip` at each element.

### Twiss Parameters

The 4D Twiss calculation essentially ignores transverse-longitudinal coupling (as do MAD and Elegant). The full 6D treatment is considerably more complex.

For **off-energy** particles, the `normalize_twiss` parameter controls whether the transfer matrix is energy-normalized by converting from $(x, p_x, y, p_y)$ to $(x, x', y, y')$ coordinates. Normalization ensures Twiss parameters are independent of reference $p_z$ in linear elements.

The **Montague W-function** characterizes chromaticity:

$$W = \sqrt{A^2 + B^2}, \quad A = \frac{\partial\alpha}{\partial p_z} - \frac{\alpha}{\beta}\frac{\partial\beta}{\partial p_z}, \quad B = \frac{1}{\beta}\frac{\partial\beta}{\partial p_z}$$

### Dispersion

Dispersion is defined as:

$$\eta_x(s) = \left.\frac{dx}{dp_z}\right|_s, \qquad \eta_y(s) = \left.\frac{dy}{dp_z}\right|_s$$

Momentum dispersion: $\eta_{px} = dp_x/dp_z$, $\eta_{py} = dp_y/dp_z$.

The dispersion derivative relates to momentum dispersion by:

$$\frac{d\eta_x}{ds} = \frac{\eta_{px}}{1+p_z} - \frac{p_x}{(1+p_z)^2}$$

Normal mode dispersion is obtained via $\boldsymbol{\eta}_a = \mathbf{V}^{-1} \boldsymbol{\eta}_x$.

For open geometry lattices, Bmad calculates **local dispersion** (with respect to local energy deviation). Non-local dispersion (with respect to initial energy) differs by a scaling factor.

### Tunes and Eigen Analysis

From the $6\times 6$ one-turn matrix, eigenvalues come in conjugate pairs:

$$\lambda_1, \lambda_2 = e^{\pm i\theta_a}, \quad \lambda_3, \lambda_4 = e^{\pm i\theta_b}, \quad \lambda_5, \lambda_6 = e^{\pm i\theta_c}$$

Mode association: the eigenvector pair with largest $x$/$p_x$ components is the a-mode (horizontal-like), largest $y$/$p_y$ is the b-mode, largest $z$/$p_z$ is the c-mode.

Positive tune convention: clockwise rotation in $(x, p_x)$ or $(y, p_y)$ space.

### Action-Angle Coordinates

The transformation $\mathbf{T} = \mathbf{N}\,\mathbf{R}\,\mathbf{N}^{-1}$ where $\mathbf{R}$ is block-diagonal with $2\times 2$ rotation matrices. In normal mode coordinates:

$$\mathbf{a} = (\sqrt{2J_a}\cos\phi_a, -\sqrt{2J_a}\sin\phi_a, \ldots)$$

Without coupling: $x = \sqrt{2J\beta}\cos\phi$, $p = -\sqrt{2J/\beta}(\alpha\cos\phi + \sin\phi)$.

---

## Synchrotron Radiation

### Radiation Damping and Excitation

Energy loss at a given location:

$$\frac{\Delta E}{E_0} = -\left[k_d \langle g^2\rangle L_p + \sqrt{k_f \langle g^3\rangle L_p}\;\xi\right](1+p_z)^2$$

where $g$ is the bending strength ($1/\rho$), $L_p$ is the path length, $\xi$ is a Gaussian random number (unit sigma), and:

$$k_d = \frac{2 r_c}{3}\gamma_0^3, \qquad k_f = \frac{55 r_c \hbar}{24\sqrt{3}\,mc}\gamma_0^5$$

with $r_c = q^2/(4\pi\epsilon_0 mc^2)$ the classical radius. Changes in momentum coordinates (assuming forward-directed emission):

$$\Delta p_x = -\frac{k_E}{1+p_z} p_x, \quad \Delta p_y = -\frac{k_E}{1+p_z} p_y, \quad \Delta p_z \approx -k_E$$

Control parameters in lattice files:
- `bmad_com[radiation_damping_on]` -- deterministic part
- `bmad_com[radiation_fluctuations_on]` -- stochastic part
- `bmad_com[radiation_zero_average]` -- shift spectrum to zero average loss

### Synchrotron Radiation Integrals

The coupled-motion radiation integrals are:

$$I_1 = \oint ds \; \mathbf{g}\cdot\boldsymbol{\eta}, \quad I_2 = \oint ds \; g^2, \quad I_3 = \oint ds \; g^3$$

$$I_{4a} = \oint ds \left[g^2 \mathbf{g}\cdot\boldsymbol{\eta}_{2a} + \nabla g^2 \cdot \boldsymbol{\eta}_{2a}\right]$$

$$I_{5a} = \oint ds \; g^3 \mathcal{H}_a, \quad \mathcal{H}_a = \gamma_a\eta_a^2 + 2\alpha_a\eta_a\eta_a' + \beta_a\eta_a'^2$$

Key derived quantities:
- Momentum compaction: $\alpha_p = I_1/L$
- Energy loss per turn: $U_0 = \frac{2 r_c E_0^4}{3(mc^2)^3} I_2$
- Damping partitions: $J_a = 1 - I_{4a}/I_2$, $J_b = 1 - I_{4b}/I_2$, $J_z = 2 + I_{4z}/I_2$
- Robinson's theorem: $J_a + J_b + J_z = 4$

### Equilibrium Emittance

Energy spread:

$$\sigma_{p_z}^2 = C_q \gamma_0^2 \frac{I_3}{2I_2 + I_{4z}}, \quad C_q = \frac{55}{32\sqrt{3}}\frac{\hbar}{mc}$$

Emittances:

$$\epsilon_a = \frac{C_q}{I_2 - I_{4a}} \gamma_0^2 I_{5a}, \qquad \epsilon_b = \frac{C_q}{I_2 - I_{4b}}\left(\gamma_0^2 I_{5b} + \frac{13}{55} I_{6b}\right)$$

The 6D transport-matrix approach to emittance calculation (using damped maps and stochastic matrices) is generally preferred over radiation integrals because it does not assume negligible synchrotron frequency and is simpler computationally.

---

## Wakefields

### Short-Range Wakes

Short-range (intra-bunch) wakes are modeled for monopole and dipole modes. The longitudinal monopole kick on trailing particle $i$:

$$\Delta p_z(i) = \frac{-eL}{v P_0}\left(\frac{1}{2}W_\parallel(0)|q_i| + \sum_{j\ne i} W_\parallel(dz_{ij})|q_j|\right)$$

The transverse dipole kick:

$$\Delta p_x(i) = \frac{-eL\sum_j |q_j| \, x \, W_\perp(dz_{ij})}{v P_0}$$

Wakes are approximated as sums of pseudo-modes for computational efficiency ($O(N)$ vs $O(N^2)$):

$$W(z) = A_a \sum_i A_i e^{d_i z} \sin(k_i z + \phi_i)$$

### Long-Range Wakes

Long-range (inter-bunch) wakes are characterized by cavity modes with $(R/Q)$ and quality factor:

$$W_i(t) = -c \, A_a \left(\frac{R}{Q}\right)_i \exp(-d_i t) \sin(\omega_i t + \phi_i)$$

The transverse kick from a mode of order $m$ has the same form as a multipole of order $n = m - 1$. Wakes are accumulated cavity-by-cavity for $O(N)$ scaling, decomposed into normal/skew and sin/cos components.

---

## Spin Dynamics

The classical spin vector $\mathbf{S}$ evolves via the modified Thomas-Bargmann-Michel-Telegdi (T-BMT) equation:

$$\frac{d\mathbf{S}}{ds} = \left\{\frac{(1+\mathbf{r}_t\cdot\mathbf{g})}{c\beta_z}(\boldsymbol{\Omega}_{BMT} + \boldsymbol{\Omega}_{EDM}) - \mathbf{g}\times\hat{\mathbf{z}}\right\} \times \mathbf{S}$$

The BMT precession vector:

$$\boldsymbol{\Omega}_{BMT} = -\frac{q}{mc}\left[\left(\frac{1}{\gamma}+a\right)c\mathbf{B} - \frac{a\gamma c}{1+\gamma}(\boldsymbol{\beta}\cdot\mathbf{B})\boldsymbol{\beta} - \left(a+\frac{1}{1+\gamma}\right)\boldsymbol{\beta}\times\mathbf{E}\right]$$

where $a = (g-2)/2$ is the anomalous magnetic moment. Bmad uses quaternion representation for spin rotations.

---

## Multiparticle Simulation

### Bunch Distributions

Bmad supports several bunch initialization methods:

**Elliptical distribution**: Phase space is partitioned into regions bounded by ellipses of constant action $J$. Within each region, particles are equally spaced in angle $\phi$. Particle charge is weighted to match a Gaussian distribution. This puts more particles in the tails (useful for studying nonlinear effects) while preserving emittance. Parameters: number of $J$ shells ($N_J$), particles per shell ($N_\phi$), and boundary sigma cutoff ($n_\sigma$).

**KV (Kapchinsky-Vladimirsky) distribution**: A 4D generalization of the elliptical distribution with a single shell in the combined $(x, p_x, y, p_y)$ space. The distribution is uniform on a 3D hypersurface of constant combined action $I_1 = \xi$:

$$\rho(I_1, I_2, \phi_x, \phi_y) = \frac{1}{A}\delta(I_1 - \xi)$$

All particles have equal weight $q = 1/N_\text{tot}$.

**Gaussian distribution**: Standard random sampling from a 6D Gaussian with specified Twiss parameters and emittances. This is the most common method for realistic simulations.

Beam tracking supports bunches organized into trains within a beam structure, with macroparticle tracking available (though currently not actively maintained).
