# To-do list

- [ ] Fix the presence of imaginary eigenfrequencies detected in the second tutorial. Proceed
      simultaneously with the overhauling of the `GASFilter` object in case the error is found there. 
- [ ] Overhaul the implementation of the `GASFilter` object:      
    - Invoke `Spring` rather than `InternalSpring`.   
    - Eliminate completely the `InternalSpring` object.
    - Move the mass of the spring and magic wand equations to the `Spring` object.
- [ ] Implement inverted pendulums.
- [ ] Implement the wire bending potential.
- [ ] Validate results by comparison with independent calculations (e.g. Pendulum Toolkit, SUMCOM) and
      assess the origin of discrepancies in they are found.
- [ ] Assess whether it is worth it to implement an eigenvector calculation in Symengine rather
      than relying on Mpmath.
- [ ] Identify the reason for the method `calculate_equilibrium_positions()` to be relatively slow.
- [ ] To avoid repeating calculations, save the results to a file so they can be loaded and used later.
- [ ] Write methods `prepare_manga()` and `show_manga()` for showing the still mechanical system right after the equilibrium positions are calculated.
