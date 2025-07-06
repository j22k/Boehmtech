# 🚀 Quick Start Guide - Boehm Tech TaskMaster

## For Linux/Mac Users

1. **Extract the project files** to your desired location
2. **Open terminal** in the project directory
3. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```
4. **Open your browser** and go to `http://localhost:5000`
5. **Login with default credentials**:
   - Username: `admin`
   - Password: `admin123`

## For Windows Users

1. **Extract the project files** to your desired location
2. **Double-click** `deploy.bat` or run it from Command Prompt
3. **Open your browser** and go to `http://localhost:5000`
4. **Login with default credentials**:
   - Username: `admin`
   - Password: `admin123`

## Manual Setup (if scripts don't work)

1. **Install Python 3.11+** if not already installed
2. **Open terminal/command prompt** in project directory
3. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```
4. **Activate virtual environment**:
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Run the application**:
   ```bash
   python src/main.py
   ```

## First Steps After Login

1. **Change the default admin password** in Profile settings
2. **Create additional users** in the Users section
3. **Create your first task** in the Tasks section
4. **Explore the dashboard** to see statistics

## Need Help?

- Check the full `README.md` for detailed documentation
- Ensure Python 3.11+ is installed
- Make sure port 5000 is not in use by another application
- For Windows users, run Command Prompt as Administrator if you encounter permission issues

## Features to Try

- ✨ **Beautiful Dark Theme** with neon accents
- 👥 **User Management** with role-based permissions
- 📋 **Task Creation** and assignment
- 📊 **Dashboard Statistics** and analytics
- 📱 **Responsive Design** - try it on mobile!
- 🔐 **Secure Authentication** with JWT tokens

---

**Welcome to Boehm Tech TaskMaster!** 🎯

