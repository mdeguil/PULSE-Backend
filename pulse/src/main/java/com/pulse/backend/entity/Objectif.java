package com.pulse.backend.entity;

import com.pulse.backend.enums.Categorie;
import com.pulse.backend.enums.StatutObjectif;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;

@Entity
@Table(name = "objectif")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Objectif {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String idObjectif;

    /** Propriétaire de l'objectif (RG-GOAL-01). */
    @Column(nullable = false)
    private String userId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Categorie categorie;

    @Column(nullable = false)
    private String libelle;

    /** Doit être strictement positive (RG-GOAL-02). */
    @Column(nullable = false)
    private double valeurCible;

    /** Ne doit jamais être négative (RG-GOAL-08). */
    @Column(nullable = false)
    private double valeurActuelle;

    @Column(nullable = false)
    private String unite;

    /** ACTIVE à la création (RG-GOAL-03). */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private StatutObjectif statut;

    private LocalDate dateDebut;

    private LocalDate dateFin;
}
