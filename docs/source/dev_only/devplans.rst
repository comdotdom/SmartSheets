Development Plans
=================
Result Storage
--------------
In early versions, the audit will save its results on the computer it is being run from.

In later versions it is our intention to write audit results back to Smartsheets.

Smartsheets account
-------------------
This was initially developed using a regular user's API key.

We ought to have a user set up with read only access to all the workspaces we want to audit.
This system user account would only exist for the purposes of auditing our Smartsheets portfolio.
When we want to audit a workspace, the workspace owner grants r/o only access to the audit account. this could be permanent to allow regular audit updates, or temporary to increase data security.

There is a risk that the audit account could be used to gain access to confidential data held in Smartsheets. Although the audit code does not read the contents of cells or the values in dashboard widgets etc, the account would have access to do so. It is vital therefore appropriate security and privacy measures are in place to control access to the account, its password and its API key.

.. todo:: Set up a SmartsheetAudit smartsheet user (agree with IT management)
