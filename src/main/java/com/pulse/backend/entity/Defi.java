package com.pulse.backend.entity;

import com.pulse.backend.enums.Categorie;
import com.pulse.backend.enums.StatutDefi;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;

@Entity
@Table(name = "defi")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Defi {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String idDefi;

    @Column(nullable = false)
    private String titre;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Categorie categorie;

    @Column(nullable = false, length = 1000)
    private String description;

    @Column(nullable = false)
    private LocalDate dateDebut;

    @Column(nullable = false)
    private LocalDate dateFin;

    @Column(nullable = false)
    private double valeurCible;

    @Column(nullable = false)
    private String unite;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private StatutDefi statut;

    @Column(nullable = false)
    private String creePar;
}
