package com.pulse.backend.entity;

import com.pulse.backend.enums.StatutParticipation;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "participation")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Participation {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String idParticipation;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "id_defi", nullable = false)
    private Defi defi;

    @Column(nullable = false)
    private String userId;

    @Column(nullable = false)
    private LocalDateTime dateInscription;

    @Column(nullable = false)
    private double valeurProgression;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private StatutParticipation statutParticipation;
}
