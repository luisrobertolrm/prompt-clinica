import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { RegistroConsultaComponent } from './pages/registro-consulta/registro-consulta.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { 
    path: '', 
    component: MainLayoutComponent,
    canActivate: [authGuard], // Protegendo todo o Shell logado
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'pep', component: RegistroConsultaComponent },
      // Redirecionamento em fallback dentro do root do painel:
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: 'login' }
];
