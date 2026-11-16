Tutorials
=========

.. warning::

    Documentation under construction   
    This section is incomplete and subject to change.

This gallery contains tutorials demonstrating how to use the Gwsus
package. The examples illustrate the construction of suspensions,
the relevant numerical calculations, and the visualization of results.

Currently, the tutorials only cover a preliminary version of KAGRA's SR2
suspension. However, when ready, more examples will be added to explain in more detail the
usage and implementation of the inverped pendulum and GAS filter objects. 

Gwsus is able to create animations of the resonance modes in a browser using
`VPython <https://vpython.org>`_, which relies on `WebGL <https://www.khronos.org/webgl/>`_
to display the graphics. You can check whether your browser is configured to support WebGL
by visiting the pages `WebGL 2 Test Page <https://get.webgl.org/webgl2/>`_ and
`WebGL Test Page <https://get.webgl.org/>`_.



Coordinate system
-----------------
This diagram shows the mirror and the axis convention used in Gwsus:

.. image:: ../_static/xyz-dark-mode.png
   :alt: Three-dimensional visualization of the mechanical system
   :class: only-dark
   :align: center
   :width: 50%


.. image:: ../_static/xyz-light-mode.png
   :alt: Three-dimensional visualization of the mechanical system
   :class: only-light
   :align: center
   :width: 50%

The positive longitudinal direction is defined by the front side of the mirror, where the
high-reflectance coating is. The positive transverse direction is defined by the righ-hand rule:
it is the direction the thumb points to when the other fingers bend from the vertical direction 
to the longitudinal one. Their equivalence to the usual *xyz* notation is:

.. math::
   :label: coordinate_equivalence

   (l,t,v) \longrightarrow (x,y,z),

where :math:`l`, :math:`t` and :math:`v` stand for longitudinal, transverse and vertical.
It is particularly important to keep in mind this convention, especially when extracting
numerical values of moments of inertia from 3D-CAD software like Autodesk Inventor, where
the :math:`y` axis points to the positive vertical direction indicated by the top face of the ViewCube.

Roll, pitch and yaw designate rotations around the longitudinal, transverse and vertical axes
respectively. Their positive directions are defined by the right-hand rule: they are the 
directions the fingers curl to when the thumb points to their respective axes' positive directions.

Physical Units
--------------
As expected, this software uses the International System of Units (SI). 
For the sake of ease of use, 
the frequencies are quantified in the derived unit of herz, rather than in
radians per second.

Tutorial list
-------------