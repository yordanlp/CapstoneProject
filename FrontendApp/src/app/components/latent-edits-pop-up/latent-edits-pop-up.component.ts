import { AfterViewInit, Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { LatentEdit } from '../../models/latent-edit.model';

@Component({
  selector: 'app-latent-edits-pop-up',
  templateUrl: './latent-edits-pop-up.component.html',
  styleUrls: ['./latent-edits-pop-up.component.css']
})
export class LatentEditsPopUpComponent implements OnInit, AfterViewInit{

  modalDialog: HTMLDialogElement | null = null;
  latentEdit: LatentEdit;
  interpolationSteps: number = 1;
  latentEdits: Array<LatentEdit> = Array();
  @Output() updateLatentEdits = new EventEmitter<{
      interpolationSteps: number
      latentEdits: Array<LatentEdit>
  }>();

  @Output() close = new EventEmitter<any>();

  constructor() {
    this.latentEdit = {
      principal_component_number: 0,
      start_layer: 0,
      end_layer: 0,
      lower_coeff_limit: 0,
      upper_coeff_limit: 0
    }
  }
  ngAfterViewInit(): void {
    this.modalDialog = document.querySelector("#modelPopup") as HTMLDialogElement;
  }
  showModal(){
    this.latentEdit = {
      principal_component_number: 0,
      start_layer: 0,
      end_layer: 0,
      lower_coeff_limit: 0,
      upper_coeff_limit: 0
    }
    if( this.modalDialog == null )
      this.modalDialog = document.querySelector("#modelPopup") as HTMLDialogElement;
    this.modalDialog?.showModal();
  }

  submitLatentEdits(){
    console.log("Latent Edits", this.latentEdits);
    this.updateLatentEdits.emit({
      interpolationSteps: this.interpolationSteps,
      latentEdits: this.latentEdits
    });
    this.latentEdit = {
      principal_component_number: 0,
      start_layer: 0,
      end_layer: 0,
      lower_coeff_limit: 0,
      upper_coeff_limit: 0
    }
    this.latentEdits = [];
    this.interpolationSteps = 1;
    this.closeModal();
  }

  addLatentEdit(): void {
    this.latentEdits.push({
      principal_component_number: this.latentEdit.principal_component_number,
      start_layer: this.latentEdit.start_layer,
      end_layer: this.latentEdit.end_layer,
      lower_coeff_limit: this.latentEdit.lower_coeff_limit,
      upper_coeff_limit: this.latentEdit.upper_coeff_limit
    });
  }


  deleteLatentEdit( index: number ): void{
    if( index >= 0 && index <= this.latentEdits.length )
      this.latentEdits.splice(index, 1);
  }

  closeModal(){
    this.modalDialog?.close();
    this.close.emit();
  }

  ngOnInit(): void {
    
  }

}
