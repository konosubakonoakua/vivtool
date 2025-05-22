import winreg
import tkinter as tk
from tkinter import ttk, messagebox
import os

class VivadoVersionSwitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Vivado Version Switcher")
        self.root.geometry("750x500")
        
        # Initialize UI
        self.create_widgets()
        self.detect_versions()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Registry structure display (exactly as in your image)
        reg_frame = ttk.LabelFrame(main_frame, text="Registry Structure (HKEY_CLASSES_ROOT)", padding="10")
        reg_frame.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, pady=5)
        
        self.registry_tree = ttk.Treeview(reg_frame, height=8, show="tree", selectmode="browse")
        self.registry_tree.pack(fill=tk.BOTH, expand=True)
        
        # Version operation area
        oper_frame = ttk.Frame(main_frame)
        oper_frame.grid(row=1, column=0, sticky=tk.NSEW, pady=5)
        
        # Current version (from registry)
        ttk.Label(oper_frame, text="Current Version:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.current_version = ttk.Label(oper_frame, text="", width=15, relief="sunken")
        self.current_version.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Target version (from installation directory)
        ttk.Label(oper_frame, text="Target Version:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_version = ttk.Combobox(oper_frame, state="readonly", width=15)
        self.target_version.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Action buttons
        ttk.Button(oper_frame, text="Detect Versions", command=self.detect_versions).grid(row=0, column=2, padx=10)
        ttk.Button(oper_frame, text="Switch Version", command=self.switch_version).grid(row=1, column=2, padx=10)
        
        # Details area
        detail_frame = ttk.LabelFrame(main_frame, text="Version Details", padding="10")
        detail_frame.grid(row=1, column=1, sticky=tk.NSEW, pady=5, padx=5)
        
        self.detail_text = tk.Text(detail_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Operation Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=5)
        
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def log_message(self, message):
        """Add message to log area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def detail_message(self, message):
        """Add message to details area"""
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, message)
        self.detail_text.config(state=tk.DISABLED)
        
    def detect_versions(self):
        """Detect versions from registry and installation directory"""
        self.log_message("Detecting Vivado versions...")
        
        # Clear existing data
        self.current_version.config(text="")
        self.target_version.set('')
        self.target_version['values'] = []
        self.registry_tree.delete(*self.registry_tree.get_children())
        
        # 1. Get current version from registry (exactly as in your image)
        current_ver = self.detect_registry_version()
        if current_ver:
            self.current_version.config(text=current_ver)
            self.log_message(f"Current registry version: {current_ver}")
        else:
            self.log_message("No Vivado version found in registry")
        
        # 2. Get available target versions from installation directory
        target_versions = self.detect_installed_versions()
        if target_versions:
            self.target_version['values'] = target_versions
            if len(target_versions) > 0:
                self.target_version.set(target_versions[0])
            self.log_message(f"Available target versions: {', '.join(target_versions)}")
        else:
            self.log_message("No Vivado versions found in installation directory")
        
        # Update registry tree display (exactly as in your image)
        self.update_registry_tree()
        
        # Show details for current version
        if current_ver:
            self.show_version_details(current_ver)
    
    def detect_registry_version(self):
        """Detect current Vivado version from registry (exactly as in your image)"""
        vivado_keys = [
            "Vivado.Checkpoint.1",
            "Vivado.Project.1",
            "Vivado.WDB.1"
        ]
        
        try:
            with winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT) as hkey:
                for key_name in vivado_keys:
                    try:
                        with winreg.OpenKey(hkey, f"{key_name}\\DefaultIcon") as key:
                            value, _ = winreg.QueryValueEx(key, "")
                            # Simple string search for version pattern (e.g. "2021.1")
                            parts = value.split("Vivado\\")
                            if len(parts) > 1:
                                version_part = parts[1].split("\\")[0]
                                if "." in version_part and version_part.replace(".", "").isdigit():
                                    return version_part
                    except WindowsError:
                        continue
            return None
        except Exception as e:
            self.log_message(f"Error detecting registry version: {str(e)}")
            return None
    
    def detect_installed_versions(self):
        """Detect installed Vivado versions from C:\\Xilinx\\Vivado"""
        install_path = r"C:\Xilinx\Vivado"
        versions = []
        
        if os.path.exists(install_path):
            try:
                for item in os.listdir(install_path):
                    full_path = os.path.join(install_path, item)
                    if os.path.isdir(full_path):
                        # Look for version pattern (e.g. "2021.1")
                        if "." in item and item.replace(".", "").isdigit():
                            versions.append(item)
                return sorted(versions, reverse=True)
            except Exception as e:
                self.log_message(f"Error detecting installed versions: {str(e)}")
                return []
        else:
            self.log_message(f"Vivado installation directory not found: {install_path}")
            return []
    
    def update_registry_tree(self):
        """Update registry tree display"""
        vivado_keys = [
            "Vivado.Checkpoint.1",
            "Vivado.Project.1",
            "Vivado.WDB.1"
        ]
        
        for key in vivado_keys:
            parent = self.registry_tree.insert("", "end", text=key)
            self.registry_tree.insert(parent, "end", text="DefaultIcon")
            shell = self.registry_tree.insert(parent, "end", text="Shell")
            self.registry_tree.insert(shell, "end", text="Open")
            self.registry_tree.insert(shell, "end", text="Command")
    
    def show_version_details(self, version):
        """Show details for specified version"""
        vivado_keys = [
            "Vivado.Checkpoint.1",
            "Vivado.Project.1",
            "Vivado.WDB.1"
        ]
        
        details = []
        
        try:
            with winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT) as hkey:
                for key_name in vivado_keys:
                    try:
                        with winreg.OpenKey(hkey, f"{key_name}\\DefaultIcon") as key:
                            value, _ = winreg.QueryValueEx(key, "")
                            details.append(f"{key_name}\\DefaultIcon:\n{value}\n")
                        
                        with winreg.OpenKey(hkey, f"{key_name}\\Shell\\Open\\Command") as key:
                            value, _ = winreg.QueryValueEx(key, "")
                            details.append(f"{key_name}\\Command:\n{value}\n")
                    except WindowsError as e:
                        details.append(f"{key_name} access failed: {str(e)}\n")
            
            self.detail_message(f"Details for version {version}:\n\n" + "\n".join(details))
        except Exception as e:
            self.detail_message(f"Error getting version details: {str(e)}")
    
    def switch_version(self):
        """Switch Vivado version (exactly as in your image)"""
        current_ver = self.current_version.cget("text")
        target_ver = self.target_version.get()
        
        if not current_ver or not target_ver:
            messagebox.showwarning("Warning", "Current or target version not specified")
            return
            
        if current_ver == target_ver:
            messagebox.showwarning("Warning", "Current and target versions are the same")
            return
            
        if not messagebox.askyesno("Confirm", f"Switch Vivado association from {current_ver} to {target_ver}?"):
            return
            
        self.log_message(f"Starting version switch: {current_ver} -> {target_ver}")
        
        # Exactly as shown in your image
        vivado_keys = [
            "Vivado.Checkpoint.1",
            "Vivado.Project.1",
            "Vivado.WDB.1"
        ]
        
        success_count = 0
        total_count = 0
        
        try:
            with winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT) as hkey:
                for key_name in vivado_keys:
                    total_count += 2  # DefaultIcon and Command
                    
                    # Process DefaultIcon (as in your image)
                    try:
                        with winreg.OpenKey(hkey, f"{key_name}\\DefaultIcon", 0, winreg.KEY_ALL_ACCESS) as key:
                            value, _ = winreg.QueryValueEx(key, "")
                            # Simple direct replacement of version string
                            new_value = value.replace(
                                f"Vivado\\{current_ver}\\", 
                                f"Vivado\\{target_ver}\\"
                            )
                            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, new_value)
                            self.log_message(f"Updated {key_name}\\DefaultIcon")
                            success_count += 1
                    except WindowsError as e:
                        self.log_message(f"Failed to update {key_name}\\DefaultIcon: {str(e)}")
                    
                    # Process Command (as in your image: Shell\Open\Command)
                    try:
                        with winreg.OpenKey(hkey, f"{key_name}\\Shell\\Open\\Command", 0, winreg.KEY_ALL_ACCESS) as key:
                            value, _ = winreg.QueryValueEx(key, "")
                            # Simple direct replacement of version string
                            new_value = value.replace(
                                f"Vivado\\{current_ver}\\", 
                                f"Vivado\\{target_ver}\\"
                            )
                            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, new_value)
                            self.log_message(f"Updated {key_name}\\Shell\\Open\\Command")
                            success_count += 1
                    except WindowsError as e:
                        self.log_message(f"Failed to update {key_name}\\Shell\\Open\\Command: {str(e)}")
                        
            # Show results
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            self.log_message(f"Version switch complete! Success rate: {success_rate:.1f}% ({success_count}/{total_count})")
            
            if success_count > 0:
                messagebox.showinfo("Success", f"Vivado version switch complete!\n\nSuccess rate: {success_rate:.1f}%")
                # Refresh display
                self.detect_versions()
            else:
                messagebox.showwarning("Warning", "No registry entries were updated")
                
        except Exception as e:
            self.log_message(f"Version switch failed: {str(e)}")
            messagebox.showerror("Error", f"Version switch failed:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VivadoVersionSwitcher(root)
    root.mainloop()