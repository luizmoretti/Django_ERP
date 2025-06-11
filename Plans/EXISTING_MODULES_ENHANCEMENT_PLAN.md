# Plano de Melhorias - Módulos Existentes

## Visão Geral

Este documento detalha as melhorias necessárias nos módulos existentes do Django ERP que estão funcionais mas precisam ser aprimorados para atender completamente aos requisitos do sistema drywall especificados em `requisitos_sistema_drywall_us.md`.

## 1. Inventory Module Enhancements

### 1.1 Product Management (apps/inventory/product/)

#### Estado Atual
- Cadastro básico de produtos
- Categorização e marcas
- Controle de preços

#### Melhorias Necessárias

##### 1.1.1 Cálculo Automático de Materiais por Área
**Prioridade:** Alta

**Funcionalidades Requeridas:**
- Fórmulas de cálculo por tipo de produto
- Configuração de fatores de perda
- Cálculo automático baseado em área (m²/ft²)
- Sugestão de materiais complementares
- Templates de cálculo por tipo de projeto

**Modelos Necessários:**
```python
# Adicionar em apps/inventory/product/models.py
class ProductCalculationFormula(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    formula_type = models.CharField(max_length=20, choices=[
        ('per_sqft', 'Per Square Foot'),
        ('per_linear_ft', 'Per Linear Foot'),
        ('per_unit', 'Per Unit'),
        ('percentage', 'Percentage of Area')
    ])
    base_quantity = models.DecimalField(max_digits=10, decimal_places=4)
    waste_factor = models.DecimalField(max_digits=5, decimal_places=2, default=0.10)  # 10% default
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class ProductBundle(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    bundle_type = models.CharField(max_length=30, choices=[
        ('drywall_basic', 'Basic Drywall Package'),
        ('drywall_premium', 'Premium Drywall Package'),
        ('finishing', 'Finishing Package'),
        ('tools', 'Tools Package')
    ])
    
class ProductBundleItem(BaseModel):
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_per_unit = models.DecimalField(max_digits=10, decimal_places=4)
    is_optional = models.BooleanField(default=False)
```

**Estimativa:** 2-3 semanas

##### 1.1.2 Especificações Técnicas
**Prioridade:** Média

**Funcionalidades Requeridas:**
- Upload de especificações técnicas (PDF)
- Fichas técnicas estruturadas
- Certificações e normas
- Instruções de instalação
- Compatibilidade entre produtos

**Modelos Necessários:**
```python
class ProductSpecification(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification_type = models.CharField(max_length=30, choices=[
        ('technical_sheet', 'Technical Sheet'),
        ('installation_guide', 'Installation Guide'),
        ('safety_sheet', 'Safety Data Sheet'),
        ('certification', 'Certification'),
        ('warranty', 'Warranty Information')
    ])
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='products/specifications/', blank=True)
    
class ProductCompatibility(BaseModel):
    primary_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compatible_with')
    compatible_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compatible_as')
    compatibility_type = models.CharField(max_length=20, choices=[
        ('recommended', 'Recommended'),
        ('compatible', 'Compatible'),
        ('not_recommended', 'Not Recommended')
    ])
    notes = models.TextField(blank=True)
```

**Estimativa:** 1-2 semanas

### 1.2 Warehouse Management (apps/inventory/warehouse/)

#### Estado Atual
- Gestão básica de armazéns
- Controle de quantidades
- Movimentações básicas

#### Melhorias Necessárias

##### 1.2.1 Inventário Físico e Contagem Cíclica
**Prioridade:** Alta

**Funcionalidades Requeridas:**
- Planejamento de inventário físico
- Contagem cíclica por categoria
- Registro de discrepâncias
- Ajustes automáticos
- Relatórios de acuracidade

**Modelos Necessários:**
```python
# Adicionar em apps/inventory/warehouse/models.py
class PhysicalInventory(BaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    inventory_type = models.CharField(max_length=20, choices=[
        ('full', 'Full Inventory'),
        ('cycle', 'Cycle Count'),
        ('spot', 'Spot Check')
    ])
    scheduled_date = models.DateField()
    actual_date = models.DateField(null=True)
    status = models.CharField(max_length=20, choices=[
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    responsible_employee = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    
class InventoryCount(BaseModel):
    physical_inventory = models.ForeignKey(PhysicalInventory, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    system_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    counted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    discrepancy = models.DecimalField(max_digits=10, decimal_places=2)
    count_date = models.DateTimeField()
    counter_employee = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
class InventoryAdjustment(BaseModel):
    inventory_count = models.OneToOneField(InventoryCount, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=20, choices=[
        ('increase', 'Increase'),
        ('decrease', 'Decrease')
    ])
    adjustment_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    approved_by = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    applied_date = models.DateTimeField(null=True)
```

**Estimativa:** 2-3 semanas

##### 1.2.2 Sugestão Automática de Reabastecimento
**Prioridade:** Média

**Funcionalidades Requeridas:**
- Algoritmo de reabastecimento baseado em histórico
- Consideração de sazonalidade
- Lead time de fornecedores
- Análise ABC de produtos
- Alertas automáticos

**Modelos Necessários:**
```python
class ReplenishmentRule(BaseModel):
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    reorder_point = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.IntegerField(default=7)
    safety_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class ReplenishmentSuggestion(BaseModel):
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2)
    suggested_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ])
    created_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
```

**Estimativa:** 2 semanas

### 1.3 Supplier Management (apps/inventory/supplier/)

#### Estado Atual
- Cadastro básico de fornecedores
- Informações de contato

#### Melhorias Necessárias

##### 1.3.1 Sistema de Avaliação de Fornecedores
**Prioridade:** Média

**Funcionalidades Requeridas:**
- Avaliação de desempenho
- Histórico de entregas
- Qualidade dos produtos
- Conformidade com prazos
- Avaliação de preços

**Modelos Necessários:**
```python
# Adicionar em apps/inventory/supplier/models.py
class SupplierEvaluation(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    evaluation_period_start = models.DateField()
    evaluation_period_end = models.DateField()
    delivery_performance = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 scale
    quality_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    price_competitiveness = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    communication = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1)
    comments = models.TextField(blank=True)
    evaluator = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    
class SupplierDeliveryHistory(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_order = models.ForeignKey('inventory.PurchaseOrder', on_delete=models.CASCADE)
    promised_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True)
    delivery_status = models.CharField(max_length=20, choices=[
        ('on_time', 'On Time'),
        ('early', 'Early'),
        ('late', 'Late'),
        ('partial', 'Partial'),
        ('failed', 'Failed')
    ])
    delay_days = models.IntegerField(default=0)
    delivery_notes = models.TextField(blank=True)
```

**Estimativa:** 2 semanas

##### 1.3.2 Termos Comerciais e Histórico de Preços
**Prioridade:** Média

**Funcionalidades Requeridas:**
- Termos de pagamento por fornecedor
- Histórico de preços por produto
- Contratos e acordos
- Descontos e promoções
- Análise de variação de preços

**Modelos Necessários:**
```python
class SupplierContract(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    contract_number = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_terms = models.CharField(max_length=50)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    contract_file = models.FileField(upload_to='supplier_contracts/', blank=True)
    
class SupplierProductPrice(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True)
    currency = models.CharField(max_length=3, default='USD')
```

**Estimativa:** 1-2 semanas

## 2. Notification System Enhancements (apps/notifications/)

### Estado Atual
- Sistema básico de notificações
- Integração com módulos existentes

### Melhorias Necessárias

#### 2.1 Notificações Multi-Canal
**Prioridade:** Alta

**Funcionalidades Requeridas:**
- Notificações por email
- Notificações por SMS
- Notificações push (navegador)
- Preferências por usuário
- Templates personalizáveis

**Modelos Necessários:**
```python
# Adicionar em apps/notifications/models.py
class NotificationChannel(BaseModel):
    name = models.CharField(max_length=50)
    channel_type = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App')
    ])
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict)  # API keys, endpoints, etc.
    
class UserNotificationPreference(BaseModel):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
class NotificationTemplate(BaseModel):
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=50)
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    subject_template = models.CharField(max_length=200)
    body_template = models.TextField()
    variables = models.JSONField(default=list)  # Available template variables
```

**Estimativa:** 2-3 semanas

## 3. Scheduler Module Enhancements (apps/scheduller/)

### Estado Atual
- Sistema básico de agendamento
- Tipos de trabalho

### Melhorias Necessárias

#### 3.1 Integração com Projetos e Equipes
**Prioridade:** Alta

**Funcionalidades Requeridas:**
- Vinculação com projetos de clientes
- Atribuição automática de equipes
- Verificação de disponibilidade
- Conflitos de agenda
- Notificações automáticas

**Modelos Necessários:**
```python
# Adicionar em apps/scheduller/models.py
class SchedullerProject(BaseModel):
    scheduller = models.ForeignKey(Scheduller, on_delete=models.CASCADE)
    customer_project = models.ForeignKey('companies.CustomerProject', on_delete=models.CASCADE)
    estimated_duration = models.DurationField()
    actual_duration = models.DurationField(null=True)
    
class SchedullerTeam(BaseModel):
    scheduller = models.ForeignKey(Scheduller, on_delete=models.CASCADE)
    team = models.ForeignKey('companies.WorkTeam', on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=[
        ('primary', 'Primary Team'),
        ('support', 'Support Team'),
        ('specialist', 'Specialist Team')
    ])
    
class SchedullerConflict(BaseModel):
    scheduller = models.ForeignKey(Scheduller, on_delete=models.CASCADE)
    conflict_type = models.CharField(max_length=20, choices=[
        ('team_busy', 'Team Not Available'),
        ('vehicle_busy', 'Vehicle Not Available'),
        ('location_conflict', 'Location Conflict'),
        ('time_overlap', 'Time Overlap')
    ])
    conflicting_schedule = models.ForeignKey(Scheduller, on_delete=models.CASCADE, related_name='conflicts')
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
```

**Estimativa:** 2 semanas

## 4. Vehicle Module Enhancements (apps/vehicle/)

### Estado Atual
- Cadastro de veículos
- Atribuição básica de motoristas

### Melhorias Necessárias

#### 4.1 Manutenção e Controle de Frota
**Prioridade:** Média

**Funcionalidades Requeridas:**
- Agendamento de manutenção
- Controle de combustível
- Histórico de reparos
- Inspeções periódicas
- Alertas de vencimento

**Modelos Necessários:**
```python
# Adicionar em apps/vehicle/models.py
class VehicleMaintenance(BaseModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=30, choices=[
        ('oil_change', 'Oil Change'),
        ('tire_rotation', 'Tire Rotation'),
        ('brake_inspection', 'Brake Inspection'),
        ('general_inspection', 'General Inspection'),
        ('repair', 'Repair')
    ])
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True)
    mileage = models.IntegerField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    service_provider = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    
class VehicleFuelLog(BaseModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField()
    odometer_reading = models.IntegerField()
    fuel_quantity = models.DecimalField(max_digits=6, decimal_places=2)
    fuel_cost = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_station = models.CharField(max_length=100, blank=True)
    driver = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
```

**Estimativa:** 2 semanas

## Cronograma de Implementação Sugerido

### Fase 1 - Funcionalidades Críticas (6-8 semanas)
1. Product Calculation Formulas (2-3 semanas)
2. Physical Inventory System (2-3 semanas)
3. Multi-Channel Notifications (2-3 semanas)

### Fase 2 - Melhorias Operacionais (4-6 semanas)
1. Supplier Evaluation System (2 semanas)
2. Scheduler Enhancements (2 semanas)
3. Replenishment Suggestions (2 semanas)

### Fase 3 - Funcionalidades Complementares (3-4 semanas)
1. Technical Specifications (1-2 semanas)
2. Vehicle Maintenance (2 semanas)
3. Supplier Commercial Terms (1-2 semanas)

## Considerações Técnicas

### Migração de Dados
- Backup completo antes de cada migração
- Scripts de migração testados em ambiente de desenvolvimento
- Plano de rollback para cada migração

### Performance
- Índices de banco de dados para novas consultas
- Cache para cálculos complexos
- Otimização de queries com select_related/prefetch_related

### Integração com Módulos Existentes
- Manter compatibilidade com APIs existentes
- Versionamento de APIs quando necessário
- Testes de regressão abrangentes

## Recursos Necessários

- **Desenvolvedores:** 2 desenvolvedores Django experientes
- **Tempo Total:** 13-18 semanas
- **Testador:** 1 QA para testes de regressão
- **DBA:** Para otimização de consultas e índices

## Riscos e Mitigações

### Riscos
- Impacto na performance do sistema
- Quebra de funcionalidades existentes
- Complexidade das fórmulas de cálculo

### Mitigações
- Desenvolvimento incremental
- Testes automatizados extensivos
- Monitoramento de performance
- Documentação detalhada das mudanças

## Benefícios Esperados

- Automação de cálculos de materiais
- Melhor controle de inventário
- Comunicação aprimorada com clientes
- Gestão eficiente de fornecedores
- Redução de erros operacionais
- Melhoria na experiência do usuário