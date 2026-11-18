# To-do list

- [ ] Overhaul the implementation of the `GASFilter` class:      
    - Move the mass of the spring and magic wand equations
      from class `InternalSpring` to class `Spring`.
    - Eliminate `InternalSpring`.
    - Invoke `Spring` rather than `InternalSpring`.
- [ ] Assess numerical error and implement remedying strategies.
- [ ] Implement inverted pendulums.
- [ ] Implement the wire bending potential.
- [ ] Validate results by comparison with independent calculations (e.g. Pendulum Toolkit, SUMCOM) and
      assess the origin of discrepancies in they are found.
- [ ] Identify the reason for the method `calculate_equilibrium_positions()` to be relatively slow.
- [ ] To avoid repeating calculations, save the results to a file so they can be loaded and used later.
- [ ] Write methods `prepare_manga()` and `show_manga()` for showing the still mechanical system right after the equilibrium positions are calculated.
