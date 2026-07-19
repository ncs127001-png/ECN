def _save_module_contract(self):
    """Guarda el contrato con nombre único module_[NAME].yaml"""
    if not self.current_file:
        return
        
    module_name = self.module_id_entry.get().replace('.', '_').lower()
    if not module_name:
        module_name = self.current_file.stem
        
    # Determinar formato (YAML por defecto, según estándar v1.0)
    use_yaml = self.format_var.get() == 'yaml'
    ext = '.yaml' if use_yaml else '.json'
    filename = f"module_{module_name}{ext}"
    
    dest_dir = self.current_file.parent
    output_file = dest_dir / filename
    
    # Construir manifiesto...
    # ... (lógica de construcción del dict)
    
    if use_yaml:
        import yaml
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(manifest_dict, f, allow_unicode=True, default_flow_style=False)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_dict, f, indent=2, ensure_ascii=False)
            
    self._log(f"✅ Contrato guardado: {filename}")
