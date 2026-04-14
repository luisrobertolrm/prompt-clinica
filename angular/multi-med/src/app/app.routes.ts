import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { RegistroConsultaComponent } from './pages/registro-consulta/registro-consulta.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { 
    path: '', 
    component: MainLayoutComponent,
    children: [
      { path: 'pep', component: RegistroConsultaComponent },
      { path: '', redirectTo: 'pep', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: 'login' }
];
