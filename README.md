# 🚀 Custom Odoo Applications Portfolio

Welcome to the master repository for production-ready Odoo modules and system extensions. This hub serves as a central portfolio for clean, highly optimized, and scalable addons engineered to enhance core enterprise business workflows.

---

## 🛠️ Core Engineering Principles

Every module housed in this repository is built from scratch adhering strictly to standard Odoo development methodologies:

* **🔒 Advanced Record Security:** Implementation of granular security groups, access control lists (ACLs), and precise record rules to ensure bulletproof data isolation.
* **🏢 Native Multi-Company Architecture:** Advanced multi-company logic filtering baked into configurations and fields to support complex enterprise structures seamlessly.
* **📈 Optimized Performance:** Clean Python backend design and efficient PostgreSQL database queries tailored to handle heavy data loads without system latency.
* **🎨 Modern UI/UX Extensions:** Seamless XML view inheritance and clean, responsive layout design to give end-users an intuitive operational interface.

---

## 📂 Repository Structure

This repository uses a monorepo layout. Each independent subdirectory at the root level represents a standalone, plug-and-play Odoo application ready for deployment:

```text
uday_odoo_apps/
├── .gitignore
├── README.md
├── [module_directory_1]/     # Custom Module Folder
│   ├── models/                # Backend Python logic
│   ├── security/              # Security groups and record rules
│   ├── static/                # Assets, icons, and descriptions
│   └── views/                 # XML layouts and menus
└── [module_directory_2]/     # Future Module Folder


⚙️ General Installation & Setup
Clone the repository directly into your custom addons workspace directory:

Bash


git clone [https://github.com/udaykiran712/uday_odoo_apps.git](https://github.com/udaykiran712/uday_odoo_apps.git)
Configure your path: Add the cloned directory path to the addons_path variable inside your Odoo configuration file (odoo.conf).

Deploy the modules:

Restart your Odoo server.

Activate Developer Mode in the backend settings.

Navigate to the Apps dashboard and click Update Apps List.

Search for the desired custom module and click Activate/Install.

💻 Professional Profile & Contact
GitHub Layout Maintenance: Managed via active Git version control.

LinkedIn: https://www.linkedin.com/in/udaykirangardas
