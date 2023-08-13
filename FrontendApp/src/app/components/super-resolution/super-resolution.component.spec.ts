import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SuperResolutionComponent } from './super-resolution.component';

describe('SuperResolutionComponent', () => {
  let component: SuperResolutionComponent;
  let fixture: ComponentFixture<SuperResolutionComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SuperResolutionComponent]
    });
    fixture = TestBed.createComponent(SuperResolutionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
