package com.pulse.backend.entity;

import com.pulse.backend.enums.Categorie;
import com.pulse.backend.enums.FrequenceRappel;
import com.pulse.backend.enums.MomentPrefere;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "preference")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Preference {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String idPreference;

    /** userId renvoyé par le service d'authentification (ex : usr-10027). */
    @Column(nullable = false, unique = true)
    private String userId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Categorie themePrioritaire;

    @Column(nullable = false)
    private boolean notifications;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private FrequenceRappel frequenceRappel;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private MomentPrefere momentPrefere;

    @Column(nullable = false)
    private boolean participationDefis;
}
