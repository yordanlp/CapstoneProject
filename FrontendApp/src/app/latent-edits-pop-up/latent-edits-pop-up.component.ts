import { Component, Input, OnInit } from '@angular/core';
import { LatentEdit } from '../models/latent-edit.model';

@Component({
  selector: 'app-latent-edits-pop-up',
  templateUrl: './latent-edits-pop-up.component.html',
  styleUrls: ['./latent-edits-pop-up.component.css']
})
export class LatentEditsPopUpComponent implements OnInit{

  modalDialog: HTMLDialogElement | null = null;
  latentEdit: LatentEdit;
  latentEdits: Array<LatentEdit> = Array();

  constructor() {
    this.latentEdit = {
      principal_component_number: 0,
      start_layer: 0,
      end_layer: 0,
      lower_coeff_limit: 0,
      upper_coeff_limit: 0
    }
  }
  showModal(){
    this.latentEdit = {
      principal_component_number: 0,
      start_layer: 0,
      end_layer: 0,
      lower_coeff_limit: 0,
      upper_coeff_limit: 0
    }
    this.modalDialog?.showModal();
  }

  submitLatentEdits(){
    console.log("Latent Edits", this.latentEdits);
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
    console.log("Here");
    this.modalDialog?.close();
  }

  ngOnInit(): void {
    this.modalDialog = document.querySelector("#modelPopup") as HTMLDialogElement;
  }

}
