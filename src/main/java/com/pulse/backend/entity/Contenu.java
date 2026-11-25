package com.pulse.backend.entity;

import com.pulse.backend.enums.Categorie;
import com.pulse.backend.enums.StatutContenu;
import com.pulse.backend.enums.TypeContenu;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "contenu")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Contenu {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String idContenu;

    @Column(nullable = false)
    private String titre;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TypeContenu type;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Categorie categorie;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private StatutContenu statut;

    private LocalDateTime datePublication;

    @Column(nullable = false)
    private LocalDateTime dateMiseAJour;

    @Column(nullable = false)
    private String auteurId;
}
