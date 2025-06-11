# Plano de Melhorias - Módulos Parcialmente Implementados

## Visão Geral

Este documento detalha as melhorias necessárias nos módulos existentes do Django ERP para alinhar com os requisitos completos do sistema drywall especificados em `requisitos_sistema_drywall_us.md`.

## 1. Customer Management Module (apps/companies/customers/)

### Estado Atual
- ✅ Cadastro básico de clientes
- ✅ Informações de contato e endereço
- ✅ Campos para classificação

### Funcionalidades Ausentes

#### 1.1 Gestão de Projetos por Cliente
**Prioridade:** Alta

**Funcionalidades Requeridas:**
- [ ] Associação de projetos a clientes
- [ ] Histórico completo de projetos
- [ ] Status de execução por projeto
- [ ] Cronograma de projetos
- [ ] Documentação técnica por projeto
- [ ] Fotos antes/depois por projeto

**Modelos Necessários:**
```python
# Em apps/companies/customers/models.py
class CustomerProject(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    expected_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES)
    project_address = models.TextField()
    
class CustomerProjectDocument(BaseModel):
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='customer_projects/documents/')
    
class CustomerProjectPhoto(BaseModel):
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE)
    photo_type = models.CharField(max_length=20, choices=[('before', 'Before'), ('after', 'After'), ('progress', 'Progress')])
    image = models.ImageField(upload_to='customer_projects/photos/')
    description = models.CharField(max_length=200, blank=True)
```

**Estimativa:** 2-3 semanas

#### 1.2 Oportunidades de Negócio e Follow-up
**Prioridade:** Média

**Funcionalidades Requeridas:**
- [ ] Registro de oportunidades de negócio
- [ ] Sistema de follow-up com lembretes
- [ ] Histórico de interações
- [ ] Classificação de leads (frio, morno, quente)
- [ ] Pesquisas de satisfação

**Modelos Necessários:**
```python
class BusinessOpportunity(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2)
    probability = models.IntegerField(choices=[(i, f"{i}%") for i in range(0, 101, 10)])
    expected_close_date = models.DateField()
    status = models.CharField(max_length=20, choices=OPPORTUNITY_STATUS_CHOICES)
    
class CustomerInteraction(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    description = models.TextField()
    next_followup = models.DateTimeField(null=True, blank=True)
    
class CustomerSatisfactionSurvey(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE, null=True)
    overall_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    service_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    quality_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(blank=True)
```

**Estimativa:** 2 semanas

#### 1.3 Melhorias no Cadastro de Clientes
**Prioridade:** Média

**Funcionalidades Requeridas:**
- [ ] Suporte a múltiplos idiomas (English, Spanish, Portuguese)
- [ ] Campos específicos para drywall (tipo de construção, frequência de projetos)
- [ ] Sistema de classificação mais detalhado
- [ ] Limite de crédito e termos comerciais
- [ ] Pessoa de contato para empresas

**Modificações Necessárias:**
```python
# Adicionar em apps/companies/customers/models.py
class Customer(BaseAddressWithBaseModel):
    # Campos existentes...
    
    # Novos campos necessários
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    customer_segment = models.CharField(max_length=50, choices=CUSTOMER_SEGMENT_CHOICES)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_terms = models.CharField(max_length=50, choices=PAYMENT_TERMS_CHOICES, default='net_30')
    contact_person_name = models.CharField(max_length=100, blank=True)
    contact_person_phone = models.CharField(max_length=20, blank=True)
    contact_person_email = models.EmailField(blank=True)
    construction_type_preference = models.CharField(max_length=50, choices=CONSTRUCTION_TYPE_CHOICES, blank=True)
    average_project_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True)
```

**Estimativa:** 1 semana

## 2. Employee Management Module (apps/companies/employeers/)

### Estado Atual
- ✅ Cadastro básico de funcionários
- ✅ Dados pessoais e profissionais
- ✅ Controle básico de presença (attendance)

### Funcionalidades Ausentes

#### 2.1 Sistema de Equipes
**Prioridade:** Alta

**Funcionalidades Requeridas:**
- [ ] Formação de equipes de trabalho
- [ ] Especialização por tipo de serviço
- [ ] Líder de equipe
- [ ] Disponibilidade de membros
- [ ] Histórico de equipes por projeto

**Modelos Necessários:**
```python
# Criar apps/companies/teams/models.py
class WorkTeam(BaseModel):
    name = models.CharField(max_length=100)
    team_leader = models.ForeignKey(Employeer, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    specialization = models.CharField(max_length=50, choices=TEAM_SPECIALIZATION_CHOICES)
    is_active = models.BooleanField(default=True)
    max_capacity = models.IntegerField(default=4)
    
class TeamMember(BaseModel):
    team = models.ForeignKey(WorkTeam, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE)
    role_in_team = models.CharField(max_length=30, choices=TEAM_ROLE_CHOICES)
    date_joined = models.DateField(auto_now_add=True)
    date_left = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

**Estimativa:** 2 semanas

#### 2.2 Métricas de Produtividade
**Prioridade:** Média

**Funcionalidades Requeridas:**
- [ ] Tracking de produtividade por funcionário
- [ ] Métricas por equipe
- [ ] Comparação de performance
- [ ] Metas individuais e de equipe
- [ ] Relatórios de produtividade

**Modelos Necessários:**
```python
class ProductivityMetric(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE)
    team = models.ForeignKey(WorkTeam, on_delete=models.CASCADE, null=True)
    metric_date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    projects_completed = models.IntegerField(default=0)
    square_feet_completed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quality_score = models.DecimalField(max_digits=3, decimal_places=1, null=True)  # 1-10 scale
    efficiency_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True)  # 1-10 scale
    
class ProductivityTarget(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(WorkTeam, on_delete=models.CASCADE, null=True, blank=True)
    target_period = models.CharField(max_length=20, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])
    target_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    target_projects = models.IntegerField(null=True)
    target_square_feet = models.DecimalField(max_digits=10, decimal_places=2, null=True)
```

**Estimativa:** 2-3 semanas

#### 2.3 Sistema de Avaliação
**Prioridade:** Baixa

**Funcionalidades Requeridas:**
- [ ] Avaliações periódicas de desempenho
- [ ] Autoavaliação
- [ ] Feedback 360 graus
- [ ] Planos de desenvolvimento
- [ ] Histórico de avaliações

**Modelos Necessários:**
```python
class PerformanceEvaluation(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE)
    evaluator = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='evaluations_given')
    evaluation_period_start = models.DateField()
    evaluation_period_end = models.DateField()
    technical_skills = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    teamwork = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    punctuality = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    quality_of_work = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1)
    comments = models.TextField(blank=True)
    development_plan = models.TextField(blank=True)
```

**Estimativa:** 2 semanas

## 3. Delivery Management Module (apps/delivery/)

### Estado Atual
- ✅ Gestão básica de entregas
- ✅ Associação com veículos

### Funcionalidades Ausentes

#### 3.1 Rastreamento em Tempo Real
**Prioridade:** Alta

**Funcionalidades Requeridas:**
- [ ] Link único de rastreamento por entrega
- [ ] Notificação automática ao cliente (email/SMS)
- [ ] Interface para cliente acompanhar entrega
- [ ] Tempo estimado de chegada atualizado
- [ ] Informações do entregador (nome, foto, contato)

**Modelos Necessários:**
```python
# Adicionar em apps/delivery/models.py
class DeliveryTracking(BaseModel):
    delivery = models.OneToOneField('Delivery', on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=50, unique=True)
    current_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    current_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    estimated_arrival = models.DateTimeField(null=True)
    last_location_update = models.DateTimeField(null=True)
    
class DeliveryNotification(BaseModel):
    delivery = models.ForeignKey('Delivery', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    sent_at = models.DateTimeField(null=True)
    delivery_status = models.CharField(max_length=20)
    tracking_link = models.URLField()
    
class DeliveryStatusHistory(BaseModel):
    delivery = models.ForeignKey('Delivery', on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
```

**Estimativa:** 3-4 semanas

#### 3.2 Gestão de Instalação
**Prioridade:** Alta

**Funcionalidades Requeridas:**
- [ ] Agendamento de instalação
- [ ] Equipes de instalação
- [ ] Checklist de instalação
- [ ] Registro de problemas
- [ ] Aprovação/assinatura do cliente
- [ ] Fotos do trabalho concluído

**Modelos Necessários:**
```python
class Installation(BaseModel):
    delivery = models.OneToOneField('Delivery', on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()
    actual_start_time = models.DateTimeField(null=True)
    actual_end_time = models.DateTimeField(null=True)
    installation_team = models.ForeignKey('companies.WorkTeam', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=INSTALLATION_STATUS_CHOICES)
    customer_signature = models.TextField(blank=True)  # Base64 encoded signature
    customer_satisfaction_rating = models.IntegerField(null=True, choices=[(i, i) for i in range(1, 6)])
    
class InstallationChecklist(BaseModel):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    checklist_item = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    completion_time = models.DateTimeField(null=True)
    notes = models.TextField(blank=True)
    
class InstallationIssue(BaseModel):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    resolution = models.TextField(blank=True)
    resolved_by = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    resolved_at = models.DateTimeField(null=True)
    
class InstallationPhoto(BaseModel):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    photo_type = models.CharField(max_length=20, choices=[('before', 'Before'), ('during', 'During'), ('after', 'After')])
    image = models.ImageField(upload_to='installations/photos/')
    description = models.CharField(max_length=200, blank=True)
```

**Estimativa:** 3-4 semanas

## 4. Melhorias Gerais de Performance e UX

### 4.1 Sistema de Notificações Aprimorado
**Prioridade:** Média

**Funcionalidades Requeridas:**
- [ ] Notificações push em tempo real
- [ ] Preferências de notificação por usuário
- [ ] Templates personalizáveis
- [ ] Múltiplos canais (email, SMS, push)
- [ ] Histórico de notificações

**Estimativa:** 2 semanas

### 4.2 Dashboard Executivo
**Prioridade:** Média

**Funcionalidades Requeridas:**
- [ ] KPIs principais em tempo real
- [ ] Gráficos de performance
- [ ] Alertas automáticos
- [ ] Relatórios executivos
- [ ] Comparações períodos anteriores

**Estimativa:** 2-3 semanas

## Cronograma de Implementação Sugerido

### Fase 1 - Prioridade Alta (6-8 semanas)
1. Customer Project Management (2-3 semanas)
2. Employee Teams System (2 semanas)
3. Real-time Delivery Tracking (3-4 semanas)

### Fase 2 - Prioridade Média (6-8 semanas)
1. Installation Management (3-4 semanas)
2. Employee Productivity Metrics (2-3 semanas)
3. Business Opportunities & Follow-up (2 semanas)

### Fase 3 - Melhorias Gerais (4-5 semanas)
1. Enhanced Notifications (2 semanas)
2. Executive Dashboard (2-3 semanas)
3. Customer Enhancements (1 semana)

## Considerações de Implementação

### Migrações de Banco de Dados
- Planejamento cuidadoso das migrações para evitar downtime
- Backup completo antes de cada migração major
- Testes em ambiente de staging

### Integrações Existentes
- Verificar impacto nas integrações atuais
- Atualizar APIs conforme necessário
- Manter backward compatibility onde possível

### Testes
- Testes de regressão para funcionalidades existentes
- Testes de performance para novas funcionalidades
- Testes de integração entre módulos

## Recursos Necessários

- **Desenvolvedores:** 2 desenvolvedores Django experientes
- **Tempo Total:** 16-21 semanas
- **Designer UX/UI:** Para interfaces de cliente e dashboards
- **Testador:** Para testes de regressão e novos features

## Riscos

- Impacto em funcionalidades existentes
- Mudanças nos padrões estabelecidos
- Performance com volume de dados crescente
- Complexidade das integrações em tempo real
