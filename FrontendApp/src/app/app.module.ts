import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RegisterComponent } from './components/register/register.component';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { APP_INITIALIZER } from '@angular/core';
import { AppConfig } from './services/app-config.service';
import { LoginComponent } from './components/login/login.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { AuthGuard } from './guards/auth.guard';
import { HomeComponent } from './components//home/home.component';
import { ClickOutsideModule } from 'ng-click-outside';
import { JwtInterceptor } from './interceptors/jwt.interceptor';
import { ImageCardComponent } from "./components/image-card/image-card.component";
import { ImageTransformComponent } from './components/image-transform/image-transform.component';
import { LatentEditsPopUpComponent } from './components/latent-edits-pop-up/latent-edits-pop-up.component';
import { CarouselComponent } from './components/carousel/carousel.component';
import { LoadingComponent } from './components/loading/loading.component';
import { SavedImagesComponent } from './components/saved-images/saved-images.component';
import { SavedImageCardComponent } from './components/saved-image-card/saved-image-card.component';
import { SuperResolutionComponent } from './components/super-resolution/super-resolution.component';
import { ToastrModule } from 'ngx-toastr';

export function initializeApp(appConfig: AppConfig) {
  return () => appConfig.load();
}

const routes: Routes = [
  { path: '', component: HomeComponent, canActivate: [AuthGuard] },
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { path: 'transform/:id', component: ImageTransformComponent, canActivate: [AuthGuard] },
  { path: 'saved', component: SavedImagesComponent, canActivate: [AuthGuard] },
  { path: 'superresolution/:id', component: SuperResolutionComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: '' }
];

@NgModule({
  declarations: [
    AppComponent,
    RegisterComponent,
    LoginComponent,
    NavbarComponent,
    HomeComponent,
    ImageCardComponent,
    ImageTransformComponent,
    LatentEditsPopUpComponent,
    CarouselComponent,
    LoadingComponent,
    SavedImagesComponent,
    SavedImageCardComponent,
    SuperResolutionComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    ClickOutsideModule,
    RouterModule.forRoot(routes),
    ToastrModule.forRoot()
  ],
  exports: [RouterModule],
  providers: [
    AppConfig,
    {
      provide: APP_INITIALIZER,
      useFactory: initializeApp,
      deps: [AppConfig], multi: true
    },
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
    AuthGuard
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
