<template>
  <v-row align="center" justify="center">
    <v-card class="mx-4" max-width="650px" v-if="items !== []">
      <v-toolbar flat>
        <v-toolbar-title>Lista de Programas</v-toolbar-title>
      </v-toolbar>
      <v-divider></v-divider>
      <v-card-text>
        <v-row align="center" justify="center">
          <v-col cols="7">
            <v-text-field
              v-model="search"
              prepend-icon="search"
              label="Pesquisar"
              single-line
              hide-details
              clearable
            ></v-text-field>
          </v-col>
          <v-col cols="5">
            <v-btn class="mt-2" block @click="newProgram">Adicionar</v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-data-table
              :headers="headers"
              :items="items"
              :search="search"
              sort-by="name"
            >
              <template v-slot:item.actions="{ item }">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-icon class="mr-2" v-on="on" @click="editProgram(item)"
                      >edit</v-icon
                    >
                  </template>
                  <span>Ver/editar Programa</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-icon
                      class="mr-2"
                      v-on="on"
                      @click="
                        $router.push({
                          name: 'programs-upload',
                          params: { id: item.id }
                        })
                      "
                    >
                      backup</v-icon
                    >
                  </template>
                  <span>Página de upload</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-icon
                      v-on="on"
                      @click="
                        $router.push({
                          name: 'programs-archive',
                          params: { id: item.id }
                        })
                      "
                      >archive</v-icon
                    >
                  </template>
                  <span>Página de arquivo</span>
                </v-tooltip>
              </template>
            </v-data-table>
          </v-col>
        </v-row>
      </v-card-text>
      <EditProgramDialog
        v-if="selectedProgram"
        v-model="programDialog"
        :program="selectedProgram"
        v-on:close-dialog="closeDialog"
        v-on:program-saved="getAllPrograms"
      ></EditProgramDialog>
    </v-card>
  </v-row>
</template>
<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import BackendServices from "@/services/BackendServices";
import Program from "@/models/program/program";
import EditProgramDialog from "@/views/admin/EditProgramDialog.vue";

@Component({
  components: { EditProgramDialog }
})
export default class ProgramsView extends Vue {
  headers = [
    { text: "Nome", value: "name", align: "left" },
    { text: "Duração", value: "maxDuration", align: "center" },
    { text: "Acções", value: "actions", align: "right" }
  ];
  items: Program[] = [];
  search = "";
  programDialog = false;
  selectedProgram: Program | null | undefined = null;

  created() {
    this.getAllPrograms();
  }

  getAllPrograms() {
    BackendServices.getAllPrograms().then(programsList => {
      this.items = programsList;
    });
  }

  editProgram(program: Program) {
    this.selectedProgram = program;
    this.programDialog = true;
  }

  newProgram() {
    this.selectedProgram = new Program();
    this.programDialog = true;
  }

  closeDialog() {
    this.selectedProgram = null;
    this.programDialog = false;
  }
}
</script>
