Introduction
============
Bento is a tool for building interactive dashboard applications, powered by
a templating engine built on `Plotly Dash <https://plotly.com/dash/>`_. It lets you
write a high-level description of your desired interactive dashboard and generates
the application code for you. By providing a set of common building blocks and
abstracting away some of the more complicated aspects, it aims to flatten the learning
curve of dashboarding!

Bento follows a few principles in its goal of improving user productivity:
 * Focus on one powerful, high-level object called the **descriptor**
 * Allow users a selection of ready-made building blocks called **banks**
 * Automatically handle component interactivity infrastructure
 * Provide a simple theming and layout experience

An analogy can be drawn between Bento and desktop computer hardware. A motherboard ties
together several different components in a way such that assembly can be performed
without advanced knowledge of each piece. The user is just tasked with understanding
what they want out of the finished product. In a similar way, creating the Bento
descriptor should be as simple as understanding what you want the dashboard to do and
then finding the right banks from the catalog. 

For some inspiration, check out some sample Bento apps in `this gallery <https://github.com/dereklarson/bento_gallery>`_.

To get a sense of what Plotly Dash can do, visit `their app gallery <https://dash-gallery.plotly.host/Portal/>`_.
