package com.pulse.backend.entity;

import com.pulse.backend.enums.TypeMetrique;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;

@Entity
@Table(name = "metrique")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Metrique {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String idIndicateur;

    @Column(nullable = false)
    private String userId;

    @Column(nullable = false)
    private LocalDate debutPeriode;

    @Column(nullable = false)
    private LocalDate finPeriode;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TypeMetrique typeIndicateur;

    @Column(nullable = false)
    private String libelle;

    @Column(nullable = false)
    private double valeur;

    @Column(nullable = false)
    private String unite;
}
